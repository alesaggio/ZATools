#pragma once

#include <string>
#include <vector>
#include <memory>
#include <map>
#include <cassert>
#include <TGraph2D.h>

#include "math.h"
#include <utility>
#include <fstream>


typedef std::pair<double, double> pair_d;
class massWindow {

    public:
        massWindow(std::string filename);
        double getValue (int n, int m, pair_d point);
        pair_d applyGlobalTransformation(pair_d ref, pair_d point);
        pair_d applyLocalTranformation(pair_d point);
        bool isInWindow(double center_x, double center_y, double size, double point_x, double point_y);
        bool isNoise(double center_x, double center_y, double size, double point_x, double point_y);

    private:
        std::string m_filename;
        std::vector<std::vector<TGraph2D>> m_matrix;

};
