#include <fstream>
#include <sstream>
#include <iostream>
#include <iomanip>
#include <vector>
#include "multiasset_hjb.hpp"

int main(int argc,char**argv) {
    if(argc!=3) return 2;
    std::ifstream in(argv[1]);std::ofstream out(argv[2]);
    if(!in||!out)return 3;
    std::array<double,12> rates{};
    std::array<std::array<double,12>,12> covariance{};
    for(std::size_t i=0;i<12;++i) {
        rates[i]=3*std::pow(60.,static_cast<double>(i%6)/5.);
        for(std::size_t j=0;j<12;++j) covariance[i][j]=i/6==j/6 ? 1. : .35;
    }
    std::string line;std::size_t count=0;double error=0;
    out<<"cpp_residual,python_residual,error\n"<<std::setprecision(17);
    while(std::getline(in,line)) {
        std::stringstream stream(line);std::string token;std::vector<double> row;
        while(std::getline(stream,token,','))row.push_back(std::stod(token));
        if(row.size()!=180)return 4;
        std::size_t k=0;std::array<int,2> q{static_cast<int>(row[k++]),static_cast<int>(row[k++])};
        std::array<double,12> z{};for(double&v:z)v=row[k++];
        std::array<std::array<double,2>,2> prices{};for(auto&r:prices)for(double&v:r)v=row[k++];
        hft3::MultiassetJet<2,12> jet;jet.dt=row[k++];jet.value=0;
        for(double&v:jet.gradient)v=row[k++];
        for(auto&r:jet.hessian)for(double&v:r)v=row[k++];
        for(double&v:jet.up)v=row[k++];for(double&v:jet.down)v=row[k++];
        double ref=row[k++];
        double value=hft3::multiasset_residual(jet,q,z,rates,covariance,prices,{});
        double diff=std::abs(value-ref);error=std::max(error,diff);++count;
        if(diff>1e-10*(1+std::abs(ref)))return 5;
        out<<value<<','<<ref<<','<<diff<<'\n';
    }
    std::cout<<"PASS "<<count<<" multiasset jet comparisons; max error="<<std::setprecision(17)<<error<<'\n';
}
