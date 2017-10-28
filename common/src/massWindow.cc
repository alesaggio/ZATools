#include "massWindow.h"
#include <iostream>
#include <json/json.h>
#include <math.h>
#include <TRandom.h>


// The purpose of this class is to see if a specific point falls inside an
// ellipse or not.
// This is done by converting ellipses to circles. I.e., given
// (x, y) point on the ellipse, get
// (x', y') point on the circle.
// |x'|     |M11  M12|   |x|      x' = M11*x + M12*y
// |  |  =  |        | * | | --> 
// |y'|     |M21  M22|   |y|      y' = M21*x + M22*y
// - Default constructor massWindow(...):       computes the elements of the transformation matrix.
// - getValue(...):     returns the interpolated value of the transformation matrix in a given point.
// - applyGlobalTransformation(...):    returns the coordinates (x', y').
// - isInWindow(...):   returns true if a point is inside the circle (false if outside).
// - isNoise(...):   returns true if a point is outside the circle (false if inside).

massWindow::massWindow(std::string filename) : m_filename(filename) {

    std::vector<std::vector<TGraph2D>> matrix;
    std::vector<TGraph2D> line1;
    std::vector<TGraph2D> line2;

    // Get the number of ellipses for TGraphs
    /*
    int n_ellipse = 0;
    std::ifstream ifile(filename);
    Json::Reader reader;
    Json::Value text;
    if (!ifile) std::cout << "ERROR OPENING FILE" << std::endl;
    if (ifile && reader.parse(ifile, text)) {
        n_ellipse = text.size();
    }
    std::cout << "n_ellipse: " << n_ellipse << std::endl;
    */

    // Declare TGraphs
    TGraph2D M11g(21);
    M11g.SetNameTitle("M11g", "M11");
 
    TGraph2D M12g(21);
    M12g.SetNameTitle("M12g", "M12");

    TGraph2D M21g(21);
    M21g.SetNameTitle("M21g", "M21");
 
    TGraph2D M22g(21);
    M22g.SetNameTitle("M22g", "M22");

    //Read json file
    std::ifstream ifile(filename);
    Json::Reader reader;
    Json::Value text;
    if (ifile && reader.parse(ifile, text)) {
        for (int i=0; i<text.size(); i++) {
 
            //CHECK THE VALUES
            const double mbb = text[i][0].asDouble();
            std::cout << "mbb: " << mbb << std::endl;
            const double mllbb = text[i][1].asDouble();
            std::cout << "mllbb: " << mllbb << std::endl;
            const double a = text[i][2].asDouble();
            std::cout << "a: " << a << std::endl;
            const double b = text[i][3].asDouble();
            std::cout << "b: " << b << std::endl;
            const double theta = text[i][4].asDouble();
            std::cout << "theta: " << theta << std::endl;
            const double MA = text[i][5].asDouble();
            std::cout << "MA: " << MA << std::endl;
            const double MH = text[i][6].asDouble();
            std::cout << "MH: " << MH << std::endl;
            if (MA > 0 && MH > 0 && theta > 0 && a > 0 && b > 0 && MH <= 1000) {
                double M11 = cos(theta)/sqrt(a);
                double M12 = sin(theta)/sqrt(a);
                double M21 = -sin(theta)/sqrt(b);
                double M22 = cos(theta)/sqrt(b);
                M11g.SetPoint(i, mbb, mllbb, M11);
                M12g.SetPoint(i, mbb, mllbb, M12);
                M21g.SetPoint(i, mbb, mllbb, M21);
                M22g.SetPoint(i, mbb, mllbb, M22);
            }
        }

        line1.push_back(M11g);
        line1.push_back(M12g);
        line2.push_back(M21g);
        line2.push_back(M22g);

        matrix.push_back(line1);
        matrix.push_back(line2);

        m_matrix = matrix;

    }
}


//Returns the [n,m] component of the gauge matrix at point (mA,mH)
double massWindow::getValue (int n, int m, pair_d point){
    
    double interpolation = m_matrix[n][m].Interpolate(point.first, point.second);
    if (interpolation != 0) std::cout << "NON-ZERO INTERP: " << interpolation << std::endl;

    double dist = 0;
    if (interpolation == 0) {
        dist = 1000000;
        std::ifstream ifile(m_filename);
        Json::Reader reader;
        Json::Value text;
        if (ifile && reader.parse(ifile, text)) {
            for (int i=0; i<text.size(); i++) {
                const double mbb = text[i][0].asDouble();
                const double mllbb = text[i][1].asDouble();
                const double a = text[i][2].asDouble();
                const double b = text[i][3].asDouble();
                const double theta = text[i][4].asDouble();
                const double MA = text[i][5].asDouble();
                const double MH = text[i][6].asDouble();
                if (MA > 0 && MH > 0 && theta > 0 && a > 0 && b > 0 && MH <= 1000) {
                    double distance = sqrt(pow(point.first-mbb, 2)+pow(point.second-mllbb, 2));
                    std::cout << "distance: " << distance << std::endl;
                    std::cout << "mbb, mllbb: " << mbb << ", " << mllbb << std::endl;
                    if (distance < dist) {
                        if (n==0 && m==0) interpolation = cos(theta)/sqrt(a);
                        else if (n==0 && m==1) interpolation = sin(theta)/sqrt(a);
                        else if (n==1 && m==0) interpolation = -sin(theta)/sqrt(b);
                        else if (n==1 && m==1) interpolation = cos(theta)/sqrt(b);
                    }
                    else {
                        interpolation = 0.;
                        dist = distance;
                    }
                }
            }
        }
    }
    return interpolation;
}


pair_d massWindow::applyGlobalTransformation(pair_d ref, pair_d point) {

    double m1 = this->getValue(0,0,ref)*point.first + this->getValue(0,1,ref)*point.second;
    double m2 = this->getValue(1,0,ref)*point.first + this->getValue(1,1,ref)*point.second;
    return std::make_pair(m1, m2);
}


pair_d massWindow::applyLocalTranformation(pair_d point) {

    return this->applyGlobalTransformation(point,point);   
}


bool massWindow::isInWindow(double center_x, double center_y, double size, double point_x, double point_y){
    
    double m1diff = point_x - center_x;
    double m2diff = point_y - center_y;
    pair_d mdiff = std::make_pair(m1diff, m2diff);
    pair_d center = std::make_pair(center_x, center_y);
    pair_d param = this->applyGlobalTransformation(center, mdiff);
    return sqrt(pow(param.first,2) + pow(param.second,2)) < size;
}


bool massWindow::isNoise(double center_x, double center_y, double size, double point_x, double point_y) {
    
    double m1diff = point_x - center_x;
    double m2diff = point_y - center_y;
    pair_d mdiff = std::make_pair(m1diff, m2diff);
    pair_d center = std::make_pair(center_x, center_y);
    pair_d param = this->applyGlobalTransformation(center, mdiff);
    return sqrt(pow(param.first,2) + pow(param.second,2)) > size;
}



