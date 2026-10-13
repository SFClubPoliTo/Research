#include <fstream>
#include <iomanip>
#include <iostream>
#include "scalar_baseline.hpp"

// CSV is offline output, not the allocation-free online policy interface.
int main(int argc,char**argv) {
    if(argc!=2) {std::cerr<<"usage: export_policy output.csv\n";return 2;}
    try {
        std::ofstream out(argv[1]);
        if(!out) throw std::runtime_error("Cannot open output");
        out<<"domain_sd,points,steps,t,q,y,theta,bid_offset,ask_offset\n"<<std::setprecision(17);
        for(int domain:{4,5,6}) for(unsigned ny:{81u,161u,241u}) {
            hft3::ScalarConfig c;
            c.y_max=domain*std::sqrt(c.var_y);c.points=ny;
            c.time_steps=9360;c.snapshot_stride=234;
            auto s=hft3::solve_scalar_baseline(c);
            hft3::ArrivalHamiltonian ham(c.control);
            const auto cells=(2*s.q_max+1)*s.points;
            for(std::size_t k=0;k<s.times.size();++k)
                for(int q=-s.q_max;q<=s.q_max;++q)
                    for(std::size_t j=0;j<s.points;++j) {
                        const auto idx=k*cells+(q+s.q_max)*s.points+j;
                        const double theta=s.history[idx];
                        out<<domain<<','<<ny<<','<<s.actual_steps<<','<<s.times[k]<<','<<q<<','<<s.y[j]<<','<<theta<<',';
                        if(q<s.q_max) out<<ham.offset(s.history[idx+s.points]-theta);
                        out<<',';
                        if(q>-s.q_max) out<<ham.offset(s.history[idx-s.points]-theta);
                        out<<'\n';
                    }
            std::cout<<"exported domain="<<domain<<" points="<<ny<<" snapshots="<<s.times.size()<<'\n';
        }
        if(!out) throw std::runtime_error("CSV write failed");
    } catch(const std::exception&e) {std::cerr<<e.what()<<'\n';return 1;}
}
