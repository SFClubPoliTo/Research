#include <fstream>
#include <iomanip>
#include <iostream>
#include "scalar_baseline.hpp"

int main(int argc, char** argv) {
    if(argc != 2) return 2;
    std::ofstream out(argv[1]);
    out << "study,domain,points,requested_steps,actual_steps,t,q,y,theta,bid,ask\n" << std::setprecision(17);
    for(int study=0; study<3; ++study) for(int k=0; k<3; ++k) {
        hft3::ScalarConfig c;
        int domain = study==1 ? 4+k : 5;
        c.y_max=domain*std::sqrt(c.var_y);
        c.points=study==1 ? 48*domain+1 : (study==2 ? 81+80*k : 241);
        c.time_steps=study==0 ? (4680u<<k) : 18720;
        c.snapshot_stride=c.time_steps/40;
        auto s=hft3::solve_scalar_baseline(c);
        hft3::ArrivalHamiltonian ham(c.control);
        auto cells=(2*s.q_max+1)*s.points;
        for(std::size_t time=0; time<s.times.size(); ++time) {
            if(time!=0 && time!=s.times.size()/2 && time!=s.times.size()-1) continue;
            for(int q=-s.q_max; q<=s.q_max; ++q) for(std::size_t j=0;j<s.points;++j) {
                if(std::abs(s.y[j]) > 2*std::sqrt(c.var_y)) continue;
                auto idx=time*cells+(q+s.q_max)*s.points+j;
                double value=s.history[idx];
                out<<study<<','<<domain<<','<<s.points<<','<<c.time_steps<<','<<s.actual_steps<<','<<s.times[time]<<','<<q<<','<<s.y[j]<<','<<value<<',';
                if(q<s.q_max) out<<ham.offset(s.history[idx+s.points]-value);
                out<<',';
                if(q>-s.q_max) out<<ham.offset(s.history[idx-s.points]-value);
                out<<'\n';
            }
        }
        std::cout << "study=" << study << " actual_steps=" << s.actual_steps << " points=" << s.points << '\n';
    }
    return out ? 0 : 1;
}
