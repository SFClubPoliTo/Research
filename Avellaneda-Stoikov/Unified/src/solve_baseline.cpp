#include <iostream>
#include <fstream>
#include <iomanip>
#include "scalar_baseline.hpp"
int main(int argc,char**argv) {
    if(argc!=2) {std::cerr<<"usage: solve_baseline output.csv\n";return 2;}
    try {
        std::ofstream out(argv[1]);if(!out) throw std::runtime_error("Cannot open output");
        out<<"points,requested_steps,actual_steps,theta_q0_y0,theta_q2_y0,min_theta,max_theta,min_u,max_u\n"<<std::setprecision(17);
        // Common time steps isolate spatial refinement; both obey the finest-grid CFL.
        for(auto ny:{61u,121u,241u}) for(auto nt:{2340u,4680u}) {
            hft3::ScalarConfig c;c.points=ny;c.time_steps=nt;
            const auto s=hft3::solve_scalar_baseline(c);
            out<<ny<<','<<nt<<','<<s.actual_steps<<','<<s.at(0,ny/2)<<','<<s.at(2,ny/2)<<','
               <<*std::min_element(s.theta.begin(),s.theta.end())<<','<<*std::max_element(s.theta.begin(),s.theta.end())<<','
               <<s.minimum_u<<','<<s.maximum_u<<'\n';
        }
        std::cout<<"Six positivity-preserving baseline solves completed\n";
    } catch(const std::exception&e) {std::cerr<<e.what()<<'\n';return 1;}
}
