"""Generate two manuscript editions and an explicit source coverage ledger."""
from pathlib import Path
import re
import json
import hashlib
import shutil
from layout import ROOT, OUTPUTS, FIGURES

WORKSPACE = ROOT.parent
SERIES = WORKSPACE.parent
INPUTS = ROOT / 'data/raw/source_freezes/manuscripts'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def escape(text):
    for a,b in [('&',r'\&'),('%',r'\%'),('_',r'\_'),('#',r'\#')]:
        text=text.replace(a,b)
    return text


def extract_body(text):
    start = text.find(r'\chapter*{Introduction and Motivation}')
    if start < 0: start=0
    end = text.find(r'\begin{references}',start)
    return text[start:end if end>=0 else len(text)]


def main():
    # The integrated authoring project supersedes the historical concatenation.
    # Keep it independent of workstation paths and preserve manual editorial work.
    authoring = ROOT / 'data/processed/manuscript_authoring'
    if authoring.exists():
        export_authoring(authoring)
        return
    ledger=[]; figures=[]; bibliography={}; unresolved=[]; listing_manifest=[]
    versions=[('hft1',INPUTS/'hft1/Article1.tex'),('hft2',INPUTS/'hft2/Article2.tex'),('hft3',INPUTS/'hft3/body.tex')]
    preamble=(INPUTS/'hft3/preamble.tex').read_text(encoding='utf-8-sig')
    preamble+=r'''
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{listings}
\usepackage{mathtools}
\usepackage{caption}
\usepackage{subcaption}
\usepackage[ruled,vlined]{algorithm2e}
\newcommand{\textcite}[1]{\cite{#1}}
\newcommand{\parencite}[1]{\cite{#1}}
\newtheorem{proposition}{Proposition}[chapter]
\newcommand{\E}{\mathbb{E}}
\newcommand{\Var}{\operatorname{Var}}
\newcommand{\Cov}{\operatorname{Cov}}
\newcommand{\R}{\mathbb{R}}
\newcommand{\dd}{\,\mathrm{d}}
\newcommand{\1}{\mathbf{1}}
\newcommand{\Texp}{\mathrm{T}}
\newcommand{\argmin}{\operatorname*{arg\,min}}
\newcommand{\safeincludegraphics}[2][]{\includegraphics[#1]{#2}}
\newcommand{\sourcecontext}[1]{\begin{tcolorbox}[colback=gray!5,colframe=gray!35,boxrule=.3pt]\small #1\end{tcolorbox}}
'''
    editions={v:OUTPUTS/f'report_{v}' for v in ['unificato','paper']}
    for folder in editions.values():
        (folder/'chapters').mkdir(parents=True,exist_ok=True)
        (folder/'img').mkdir(exist_ok=True)
        logo=INPUTS/'hft3/img/Logo_SFClub_Polito.png'
        shutil.copy2(logo,folder/'img/Logo_SFClub_Polito.png')
        shutil.copy2(ROOT/'data/processed/Copertina_research.pdf',folder/'Copertina_research.pdf')
        selected=preamble
        if folder==editions['paper']:
            selected=selected.replace(r'\documentclass[a4paper,10pt,titlepage,oneside,openany]{book}',r'\documentclass[a4paper,10pt,titlepage,oneside]{article}')
            selected=selected.replace('[chapter]','[section]')
            selected=selected.replace(r'\chapter*{Bibliography}',r'\section*{Bibliography}').replace('{toc}{chapter}{Bibliography}','{toc}{section}{Bibliography}')
            selected='\n'.join(line for line in selected.splitlines() if '\\patchcmd{\\@makechapterhead}' not in line and '\\patchcmd{\\@makeschapterhead}' not in line)+'\n'
        (folder/'preamble.tex').write_text(selected,encoding='utf-8')
    def adapt(text, article, source):
        text=re.sub(r'\\(label|ref|eqref)\{([^}]+)\}',lambda m:'\\'+m[1]+'{'+article+'-'+m[2]+'}',text)
        def image(m):
            path=m[3]; opts=m[2] or ''
            origin=source.parent/path
            if not origin.exists():
                article_root=INPUTS/article
                choices=list(source.parent.rglob(Path(path).name))+list(article_root.rglob(Path(path).name))
                if not choices and not Path(path).suffix:
                    choices=list(source.parent.rglob(Path(path).name+'.png'))
                origin=choices[0] if choices else origin
            if not origin.exists():
                unresolved.append({'source':str(source),'image':path})
                return r'\fbox{\parbox{.8\textwidth}{Preserved source figure: '+escape(path)+r'. Reconstruction pending.}}'
            name=article+'-'+re.sub('[^a-zA-Z0-9_-]','_',origin.stem)+origin.suffix
            for folder in editions.values(): shutil.copy2(origin,folder/'img'/name)
            figures.append({'source':origin.relative_to(ROOT).as_posix(),'sha256':sha(origin),'target':'img/'+name,'article':article})
            return r'\includegraphics'+opts+'{img/'+name+'}'
        text=re.sub(r'\\(safeincludegraphics|includegraphics)(\[[^\]]*\])?\{([^}]+)\}',image,text)
        for env in ['lstlisting','verbatim']:
            def relocate_listing(match):
                name=f'{article}-{env}-{len(listing_manifest)+1:02d}.txt'
                destination=ROOT/'data/raw/source_freezes/latex_listings'/name
                destination.parent.mkdir(parents=True,exist_ok=True)
                destination.write_text(match[0],encoding='utf-8')
                listing_manifest.append({'source':source.relative_to(ROOT).as_posix(),'destination':destination.relative_to(ROOT).as_posix(),'sha256':sha(destination),'treatment':'source listing preserved outside the article; surrounding mathematical explanation retained'})
                return ''
            text=re.sub(r'\\begin\{'+env+r'\}.*?\\end\{'+env+r'\}',relocate_listing,text,flags=re.S)
        text=re.sub(r'\\begin\{summary\}.*?\\end\{summary\}','',text,flags=re.S)
        text=re.sub(r'\\chapter\*?\{Conclusion\}',r'\\section*{Historical interpretation and limitations}',text)
        text=text.replace(r'\addcontentsline{toc}{chapter}{Conclusion}','').replace(r'\markboth{Conclusion}{Conclusion}','')
        text=re.sub(r'\\chapter\{Appendix: Companion Notebook\}.*', '', text,flags=re.S)
        text=text.replace('INSERIRE LINK GITHUB','Local supporting code; publication URL not assigned')
        text=text.replace('the HJB is preferable in all three regimes','the historical tables report improved risk-sensitive metrics in all three simulated regimes')
        text=text.replace('the HJB remains clearly superior','the historical sample favors the HJB')
        text=text.replace('the HJB, however, dominates','the historical sample, however, favors the HJB')
        text=text.replace('As \\(N\\) increases, the grid becomes finer and the empirical statistics of the simulated process tend to align more closely with the theoretical ones.', 'Increasing \\(N\\) refines time resolution. Agreement of empirical covariance with its theoretical target also depends on path count, validity of the embedding and sampling error; time-grid refinement alone does not guarantee closer empirical statistics.')
        text=text.replace('A Baseline Mid-Price Model and CARA Utility: Why Closed Forms Appear','Diffusive Prices and CARA Utility')
        text=text.replace('The Hamilton--Jacobi--Bellman Equation and Optimal Spreads','The HJB Equation and Optimal Spreads')
        text=text.replace('The Hamilton-Jacobi-Bellman Equation and Optimal Spreads','The HJB Equation and Optimal Spreads')
        text=text.replace('Two quoting paradigms: naive symmetric vs inventory-based','Symmetric and Inventory-Sensitive Quoting')
        text=text.replace('Illustrative Two-Asset Diagnostic Example: Inventory Pressure and Correlated Paths','Two-Asset Inventory Pressure and Correlated Paths')
        text=text.replace('Intraday Inventory Excursions','Inventory Dispersion')
        text=text.replace(r'\chapter*{Introduction and Motivation}',r'\section*{Motivation and transition}')
        text=text.replace(r'\addcontentsline{toc}{chapter}{Introduction and Motivation}','')
        text=text.replace(r'\markboth{Introduction and Motivation}{Introduction and Motivation}','')
        text=text.replace(r'\mainmatter','').replace(r'\frontmatter','')
        text=re.sub(r'\\setcounter\{page\}\{[^}]+\}|\\pagenumbering\{[^}]+\}', '',text)
        if article=='hft2':
            text=re.sub(r'\\miniabstract\{[^}]*\}', '',text,count=1)  # Same roadmap already supplied by the common bridge.
            text=text.replace("The next chapter begins from the first layer of that route: fractional Brownian motion. Starting there keeps the paper aligned with the first HFT article's progression from market-making motivation to mathematical engine and then to numerical validation.", '')
        if article=='hft3':
            text=text.replace('specified in Chapter 3','specified in the full lifted model below')
            text=text.replace('derived independently in Chapter 3','derived independently in the full lifted model section')
            text=text.replace('chain rule from Chapter 1','chain rule of the scalar embedding')
            text=text.replace('The next chapter records the proposed correction architecture.','The following section records the proposed correction architecture.')
            text=text.replace(r'\chapter{From HFT2 to the Reduced-HJB Residual Problem}',r'\chapter{Lifted HJB and State-Compression Defects}')
            text=text.replace(r'\chapter{The Navier--Stokes Correction Architecture}',r'\section{Source-Unverified Architectural Motivation}')
            text=text.replace(r'\chapter{Full Lifted Rough-Volatility HJB}',r'\section{Full Lifted Rough-Volatility HJB}')
            text=text.replace(r'\section{State dynamics and objective}',r'\subsection{State dynamics and objective}')
            text=text.replace(r'\section{The operator and bounded controls}',r'\subsection{The operator and bounded controls}')
            text=text.replace(r'\chapter{Residual Decomposition of State Compression}',r'\section{Residual Decomposition of State Compression}')
            text=text.replace(r'\chapter{Correction Families and Preservation Constraints}',r'\chapter{Structured Corrections and Numerical Operators}\section{Correction Families and Preservation Constraints}')
            text=text.replace(r'\chapter{Localized Iterative HJB Correction}',r'\section{Localized Iterative HJB Correction}')
            text=text.replace(r'\chapter{C++ Operators and Offline Policy Export}',r'\section{C++ Operators and Offline Policy Export}')
            text=text.replace(r'\chapter{Initial Numerical Audit}',r'\chapter{Baseline Construction and Numerical Audit}')
            text=text.replace(r'\chapter{Results and Limitations}',r'\section{Scope of the Initial Evidence}')
        text=text.replace('Davies--Harte Simulation and Validation Code','Davies--Harte Simulation and Validation')
        text=text.replace('Companion Notebook Design','Implementation Design')
        text=text.replace('Low-Latency C++ Realization','C++ Operators and Offline Policy Export')
        text=text.replace('no confidence interval for that nonlinear statistic has been computed','the conditional bootstrap interval for this nonlinear statistic is reported in the shared diagnostics chapter')
        text=text.replace("The first code increment establishes the offline residual evaluator and derivative-aware correction interfaces. It does not yet replace the starter's artificial quote surfaces with a solved policy.", 'The operator implementation supplies an offline residual evaluator and derivative-aware correction interfaces. Historical artificial demonstration surfaces remain archived separately from the solved time-dependent baseline developed below.')
        text=text.replace('The original demonstration still uses synthetic surfaces without a time coordinate.', 'The archived original demonstration used synthetic surfaces without a time coordinate.')
        text=text.replace('companion notebook','supporting simulation').replace('Companion notebook','Supporting simulation')
        text=text.replace('the first article','the classical baseline').replace('the second article','the rough-state extension')
        text=text.replace('This first article','The classical baseline').replace('the next article','the residual analysis')
        # Generated source files are documented in the code README, not the article.
        text=re.sub(r'\\texttt\{[^}]*\.(?:py|ipynb)[^}]*\}', 'the supporting implementation', text)
        text=re.sub(r'\\texttt\{[^}]*notebook[^}]*\}', 'the supporting implementation', text, flags=re.I)
        return text
    source_files=[]
    for article,source in versions:
        raw=source.read_text(encoding='utf-8-sig');source_files.append(source)
        for match in re.finditer(r'\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem|\\end\{references\})',raw,re.S):
            if match[1]=='code':continue
            bibliography.setdefault(match[1],match[2].strip())
        body=extract_body(raw)
        if article=='hft3':
            multi=INPUTS/'hft3/multiasset.tex'
            body=body.replace(r'\input{multiasset}',multi.read_text(encoding='utf-8-sig'))
            source_files.append(multi)
        for n,block in enumerate(re.split(r'\n\s*\n',body)):
            if not block.strip():continue
            ledger.append({'id':f'{article}-block-{n:04d}','source':source.relative_to(ROOT).as_posix(),'source_sha256':sha(source),
                           'block_sha256':hashlib.sha256(block.encode()).hexdigest(),'source_excerpt':block[:220],
                           'unified_destination':f'chapters/{article}.tex','paper_destination':'condensed synthesis; complete exposition in unified study',
                           'treatment':'executable listings and post-conclusion summary relocated to preserved source/code; other text integrated with source-context qualifications',
                           'scientific_status':'historical source claim' if article!='hft3' else 'working evidence or proposed method'})
        context={'hft1':'The classical baseline fixes the accounting and execution mechanism before changing the price dynamics and adding covariance-aware inventory control. Its historical configuration is distinct from the terminal-liquidation model developed next.',
                 'hft2':'The classical control problem now gains a volatility state with memory. Fractional covariance, causal Volterra kernels and finite-factor lifting lead to a reduced HJB with terminal liquidation. Historical results from the legacy clipped solver remain distinct from the positive-baseline results that follow.',
                 'hft3':'The full lifted operator and derivative-aware correction design extend the preceding models. The covariance proxy remains distinct from fitted P3. The proposed Navier--Stokes mapping is source-unverified; it supplies no theorem for the financial HJB.'}[article]
        body=adapt(body,article,source)
        body=r'\sourcecontext{'+context+'}\n'+body
        (editions['unificato']/'chapters'/f'{article}.tex').write_text(body.replace('}\\n','}\n'),encoding='utf-8')
    # Retain the expanded finite-horizon derivation unique to the alternate HFT1 source.
    alternate=ROOT/'data/raw/source_freezes/historical_article1_alternate.tex'
    alt=alternate.read_text(encoding='utf-8-sig')
    start=alt.find(r'\chapter{Classical Diffusions under a Finite Horizon}')
    end=alt.find(r'\chapter{Simulation and Experimental Design}',start)
    variant=''  # The supplied Article1 already contains this expanded chapter.
    (editions['unificato']/'chapters/classical_extension.tex').write_text(adapt(variant,'hft1-alt',alternate),encoding='utf-8')
    ledger.append({'id':'hft1-alternate','source':alternate.relative_to(ROOT).as_posix(),'source_sha256':sha(alternate),
                   'unified_destination':'full classical exposition from supplied Article1.tex; remaining historical variant in source delivery','paper_destination':'model assumptions and unified-reference credit',
                   'treatment':'supplied complete source supersedes partial variant for synthesis; full alternative source preserved','scientific_status':'historical source variant'})
    audit=json.loads((OUTPUTS/'validation/20261013-full-residual/summary.json').read_text())
    refinement=json.loads((OUTPUTS/'validation/20261013-refinement/summary.json').read_text())
    bootstrap=json.loads((OUTPUTS/'validation/cara-bootstrap.json').read_text())
    refinement_rows='\n'.join(f"{row['study'].replace('_',' ')} & {row['configuration']} & {row['errors_against_finest']['theta']:.7f} & {max(row['errors_against_finest']['bid'],row['errors_against_finest']['ask']):.7f} \\\\" for row in refinement['comparisons'] if row['errors_against_finest']['theta']>0)
    results=rf'''
\chapter{{Shared numerical diagnostics and interpretation}}
The common runtime reproduces the separate baseline and covariance-aware proxy without changing the historical model equations. Across 5,000 off-grid offset comparisons, the maximum refactoring discrepancy is $5.33\times10^{{-15}}$. These checks concern software equivalence, not HJB optimality.
\section{{A stochastic-covariance residual diagnostic}}
For $\theta_{{sep}}=\theta_0(t,q_A,Y_A)+\theta_0(t,q_B,Y_B)$ and $C=-\gamma(T-t)\Sigma_{{AB}}q_Aq_B$, the complete operator is evaluated with $\partial_t C$, $\nabla C$, $D^2 C$, mixed factor covariances and changed nonlinear arrival gains. Since $\Sigma_{{AB}}\propto\exp(\beta(Y_A+Y_B)/2)$, $\partial_{{Z_{{im}}}}C=(\beta w_m/2)C$ and $D^2 C=Caa^\top$, with $a_{{im}}=\beta w_m/2$. The covariance terms cannot be discarded as if the covariance were fixed over the control horizon.
On {audit['interior_samples']} held-out interior states from {audit['samples']} samples (seed 20261013), the sum of reduced-operator residuals has RMS {audit['reduced_sum']['rms']:.6f}; the full separate-policy residual has RMS {audit['full_separate']['rms']:.6f}; the full covariance-proxy residual has RMS {audit['full_covariance_proxy']['rms']:.6f}. The proxy therefore worsens this diagnostic. A current-covariance hedge is not a full residual correction.
The baseline derivatives are reconstructed by cubic time/state splines from the existing export. This diagnostic is not an independently converged reference solution, a bound on value error, or a certification of derivative convergence. It does not justify fitting P3 before the remaining numerical gates.
\section{{Separated refinement and sampling uncertainty}}
Nine positive-baseline solves separate temporal refinement (4680/9360/18720 effective steps at 241 nodes and 5SD), fixed-spacing domain refinement (4/5/6SD with 193/241/289 nodes) and spatial refinement (81/161/241 nodes at 5SD). Non-reference configurations are compared below with the finest configuration in their family, at $t=0,0.5$, over every inventory and common interior interpolation points. These are finite-resolution differences, not rigorous errors.
\begin{{table}}[ht]\centering\small
\begin{{tabular}}{{lrrr}}\toprule Study & Configuration & Max value diff. & Max offset diff.\\\midrule
{refinement_rows}
\bottomrule\end{{tabular}}
\caption{{Refinement in separate directions. Configuration is step count, domain SD, or node count according to the study.}}
\end{{table}}
For the two-asset experiment, 10,000 paired bootstrap resamples give a covariance-minus-separate certainty-equivalent difference {bootstrap['ce_difference']:.6f}, with percentile 95\% interval $[{bootstrap['ce_difference_95_interval'][0]:.6f},{bootstrap['ce_difference_95_interval'][1]:.6f}]$. The interval contains zero: the negative sample difference does not establish a population utility loss. This is conditional sampling uncertainty, not model/parameter uncertainty.
The preceding classical generator freeze used 1000 multivariate paths and a different correlation matrix. A separate replay now uses the supplied 3000-path configuration, with correlations $\rho_{{AB}}=0.65$, $\rho_{{AC}}=-0.55$ and $\rho_{{BC}}=-0.35$. It reproduces mean terminal PnL 158.709/154.556, PnL standard deviation 16.439/10.547, gross terminal inventory 21.949/11.203 and terminal risk norm 17.051/7.419 to the article's displayed rounding. The scalar 5000-path ABM/GBM figures also reproduce their reported summary statistics. Earlier configurations remain separately preserved.
\section{{Reproducibility and source boundaries}}
The historical variants are retained as separate scientific configurations. The full classical exposition and the rough-state exposition use the complete sources supplied by their author; their contents are not inferred from the earlier abbreviated drafts. The source archive and correspondence records retain documentary differences without changing the numerical evidence presented here.
The study concerns synthetic inventory control. Queue position, adverse selection, fee/slippage structure beyond the declared terminal cost, market calibration and exchange latency are outside the tested model. No fitted localized residual policy or verified Navier--Stokes theorem is claimed.
The finite-factor comparisons at $H=0.8$ are phenomenological configurations. The positive exponential-mixture identity for the singular rough kernel has $H<0.5$; it must not be extended to $H=0.8$ by relabeling a decreasing finite mixture. Complete-operator derivatives agree between Python and C++ on 3000 exported jets to maximum absolute difference $1.67\times10^{{-13}}$, which checks the operator implementation rather than convergence of the reconstructed derivatives.
\chapter*{{Conclusion}}
\addcontentsline{{toc}}{{chapter}}{{Conclusion}}
The series links classical inventory-sensitive quoting to causal rough-state construction, finite lifting and full-HJB diagnostics of state compression. The positive scalar baseline supports reproducible policy application; the two-asset experiment exposes a risk--revenue trade-off. The covariance proxy lowers integrated inventory risk in the reported experiment while lowering mean liquidated PnL and sample CARA certainty equivalent, and it worsens the present off-grid residual diagnostic. These outcomes motivate validation of state compression and derivatives before any fitted correction or online-efficiency claim. The supporting original material remains preserved; source correspondence and the remaining convergence gates are explicit limits of this synthesis.
'''
    (editions['unificato']/'chapters/current_results.tex').write_text(results,encoding='utf-8')
    aliases={'as':'AvellanedaStoikov2008','multiapprox':'BergaultEvangelistaGueantVieira2022','Gueant2017':'Gueant2016'}
    for alias,key in aliases.items():
        if alias in bibliography:
            bibliography.setdefault(key,bibliography[alias]);bibliography.pop(alias)
    bibliography['AbiJaberElEuch2019']=r'E. Abi Jaber and O. El Euch, \emph{Multifactor approximation of rough volatility models}, SIAM Journal on Financial Mathematics 10(2), 309--349, 2019. \url{https://arxiv.org/abs/1801.10359}.'
    bibliography['hft2']=bibliography['hft2'].replace('unpublished working manuscript supplied to this project','complete manuscript supplied by the authors')
    bibliography['sharedcode']=r'Market Making completo, local reproducibility package accompanying this study. Starting Finance Club PoliTo, Research. Project GitHub publication link pending; code is delivered locally with this research synthesis.'
    for folder in editions.values():
        for tex in folder.rglob('*.tex'):
            if tex.name=='preamble.tex':continue
            content=tex.read_text(encoding='utf-8')
            for alias,key in aliases.items():content=re.sub(r'(?<=\{)'+re.escape(alias)+r'(?=[,}])',key,content)
            tex.write_text(content,encoding='utf-8')
    refs='\\begin{references}\n'+''.join('\\bibitem{'+k+'} '+v+'\n\n' for k,v in bibliography.items())+'\\end{references}\n'
    (editions['unificato']/'references.tex').write_text(refs,encoding='utf-8')
    paper_body=(editions['paper']/'paper_body.tex').read_text(encoding='utf-8')
    paper_body=paper_body.replace(r'\chapter',r'\section').replace('{toc}{chapter}','{toc}{section}')
    (editions['paper']/'paper_body.tex').write_text(paper_body,encoding='utf-8')
    cited=set()
    for keys in re.findall(r'\\cite\{([^}]+)\}',paper_body):cited.update(keys.split(','))
    cited.update(['hft1','hft2','sharedcode'])
    paper_refs='\\begin{references}\n'+''.join('\\bibitem{'+key+'} '+value+'\n\n' for key,value in bibliography.items() if key in cited)+'\\end{references}\n'
    (editions['paper']/'references.tex').write_text(paper_refs,encoding='utf-8')
    def front(edition,abstract):
        return r'''\input{preamble}
\begin{document}
\includepdf[pages=1,fitpaper=true,pagecommand={\thispagestyle{empty}}]{Copertina_research.pdf}
\begin{titlepage}\thispagestyle{empty}\begin{center}
\includegraphics[width=2.4cm]{img/Logo_SFClub_Polito.png}\par\vspace{.7cm}
{\LARGE\bfseries High-Frequency Market Making:\\Models, Rough States and Numerical Control\par}\vspace{.3cm}
{\large '''+edition+r'''\par}\vspace{.5cm}
Research synthesis of HFT1--HFT3\\
Original contributions: Salvatore Gabriele Messina and Niccol\`o Soriano (HFT1/HFT2); Salvatore Gabriele Messina (HFT3).\\[.3cm]
Revision: 13 October 2026. Publication date not assigned.\\[.4cm]
Starting Finance Club PoliTo\\
\url{https://github.com/StartingFinanceClubPoliTo/Research}
\end{center}\begin{tightabstract}'''+abstract+r'''\end{tightabstract}\end{titlepage}
\tableofcontents
'''
    intro=r'''\chapter*{Introduction and scope}\addcontentsline{toc}{chapter}{Introduction and scope}
This study follows one control problem through three representations: classical diffusive prices, a causal lifted rough-volatility state, and residual diagnostics of a scalar policy embedded in a higher-dimensional HJB. Inventory, cash and terminal liquidation supply the common economic accounting. Model conventions and historical configurations remain distinct wherever their assumptions differ.
The first part develops the baseline market-making problem. The next establishes fractional covariance, Volterra causality and finite lifting. The final part examines the loss of information induced by scalar compression and a two-asset covariance proxy. The scientific contribution currently supported is diagnostic: a hedge that lowers a portfolio-risk statistic need not improve utility or the complete HJB residual. It is not a claim of fitted correction optimality or low exchange latency.
'''
    abstract='We unify classical inventory-sensitive market making, causal rough-state construction and finite-factor HJB diagnostics. A shared reproducibility pipeline preserves historical source versions and separates clipped legacy solves from a positive bounded-control baseline. In a synthetic two-asset experiment, a covariance proxy reduces integrated inventory risk but lowers mean PnL and sample CARA certainty equivalent; a new off-grid full-operator diagnostic also increases. These results distinguish a covariance hedge from a fitted residual correction. Source correspondence and convergence limits remain explicit.'
    unified=front('Unified study',abstract)+intro+'\n'+''.join(r'\input{chapters/'+name+'}\n' for name in ['hft1','classical_extension','hft2','hft3','current_results'])+r'\input{references}\end{document}'
    (editions['unificato']/'Articolo.tex').write_text(unified.replace('}\\n','}\n'),encoding='utf-8')
    (ROOT/'data/processed/provenance/content-coverage.json').write_text(json.dumps(ledger,indent=2),encoding='utf-8')
    local_inventory=WORKSPACE/'Utilities-Progetto/Inventari'
    if local_inventory.exists():
        (local_inventory/'content-coverage.json').write_text(json.dumps(ledger,indent=2),encoding='utf-8')
    (ROOT/'data/processed/provenance/figure-manifest.json').write_text(json.dumps(figures,indent=2),encoding='utf-8')
    (ROOT/'data/processed/provenance/relocated-listings.json').write_text(json.dumps(listing_manifest,indent=2),encoding='utf-8')
    (ROOT/'data/processed/provenance/report-source-manifest.json').write_text(json.dumps({'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in source_files], 'unresolved_images':unresolved,'coverage_status':'All source blocks retained or explicitly relocated; supplied-source/PDF identity not certified'},indent=2),encoding='utf-8')
    (editions['paper']/'Articolo.tex').write_text(front('Condensed paper',abstract).replace(r'\tableofcontents','')+r'\input{paper_body}\input{references}\end{document}',encoding='utf-8')
    print(json.dumps({'covered_source_blocks':len(ledger),'figure_inclusions':len(figures),'missing_images':unresolved,'bibliography_items':len(bibliography)},indent=2))


def export_authoring(authoring):
    for edition in ['unificato', 'paper']:
        destination = OUTPUTS / f'report_{edition}'
        destination.mkdir(parents=True, exist_ok=True)
        pending = [Path(edition + '.tex')]
        visited = set()
        while pending:
            relative = pending.pop()
            if relative in visited:
                continue
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Nonportable authoring dependency ' + str(relative))
            visited.add(relative)
            source = authoring / relative
            if not source.is_file():
                raise FileNotFoundError(source)
            target = destination / ('Articolo.tex' if relative.name == edition + '.tex' and len(relative.parts) == 1 else relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            if source.suffix != '.tex':
                continue
            text = re.sub(r'(?<!\\)%[^\n]*', '', source.read_text(encoding='utf-8'))
            for name in re.findall(r'\\(?:input|include|includegraphics|includepdf)(?:\[[^\]]*\])?\{([^}]+)\}', text):
                if '#' in name:
                    continue
                item = Path(name)
                pending.append(item if item.suffix else item.with_suffix('.tex'))
    print('Integrated manuscripts exported from the preserved authoring snapshot')


if __name__=='__main__':main()
