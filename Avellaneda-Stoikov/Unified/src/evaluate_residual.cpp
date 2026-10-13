#include <fstream>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <string>
#include <vector>
#include "full_hjb_residual.hpp"
// Whitespace input from the audited HFT2 exporter; no market or private data.
int main(int argc,char** argv) {
    if(argc!=2) {std::cerr<<"usage: evaluate_residual samples.txt\n";return 2;}
    try {
        std::ifstream in(argv[1]); if(!in) throw std::runtime_error("Cannot open input");
        std::array<double,6> rates{}, weights{};
        for(auto& x:rates) if(!(in>>x)) throw std::runtime_error("Invalid rates");
        for(auto& x:weights) if(!(in>>x)) throw std::runtime_error("Invalid weights");
        hft3::FullHjbResidual<6> residual(rates);
        std::cout<<"sample,residual,python_reference,absolute_error\n"<<std::setprecision(17);
        std::size_t count=0; int q;
        while(in>>q) {
            std::array<double,6> z{}; double v,value,dt,dy,dyy,up,down,reference;
            for(auto& x:z) if(!(in>>x)) throw std::runtime_error("Invalid state");
            if(!(in>>v>>value>>dt>>dy>>dyy>>up>>down>>reference)) throw std::runtime_error("Truncated sample");
            auto jet=hft3::embed_scalar(weights,value,dt,dy,dyy,up,down);
            const double actual=residual.evaluate(q,z,v,jet).total();
            const double error=std::abs(actual-reference);
            if(!std::isfinite(reference) || error>1e-9*(1+std::abs(reference))) throw std::runtime_error("Cross-language residual mismatch");
            std::cout<<count++<<','<<actual<<','<<reference<<','<<error<<'\n';
        }
        if(!in.eof() || count==0) throw std::runtime_error("Invalid or empty samples");
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
