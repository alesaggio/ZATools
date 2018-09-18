#!/usr/bin/env bash

get_legend() {

    local legend=""
    case $1 in
        800_400)
            legend="rho steps for 800,400" ;;

    esac

    echo $legend
}

get_legend_2d() {
    legend=$(get_legend $1)
    echo "${legend}, m_{jj} bins"
}

signals="MH-800_MA-200 MH-1000_MA-200 MH-800_MA-50 MH-500_MA-400 MH-800_MA-100 MH-650_MA-50 MH-250_MA-50 MH-1000_MA-50 MH-500_MA-50 MH-800_MA-400 MH-500_MA-300 MH-300_MA-100 MH-500_MA-200 MH-250_MA-100 MH-1000_MA-500 MH-300_MA-50 MH-800_MA-700 MH-200_MA-100 MH-200_MA-50 MH-300_MA-200 MH-500_MA-100"

flavors="MuMu ElEl MuEl"

for flavor in $flavors; do
  for signal in $signals; do

    root="postFitShapes/${signal}/$flavor"
    output="postFitPlots/${signal}/$flavor"
    
    input="${root}"

    legend=$(get_legend $signal)
    legend_2d=$(get_legend_2d $signal)

    sed "s|#ROOT#|${input}|g" centralConfig_shapes_postfit.yml.tpl > centralConfig_shapes_postfit.yml

    # Uncomment signal point
    cp MCFiles_shapes_postfit.yml.tpl MCFiles_shapes_postfit.yml
    sed -i "/,+7 s/#//" MCFiles_shapes_postfit.yml

    # Replace signal and legend
    sed "s/#SIGNAL#/${signal}/g" postfitPlots.yml.tpl > postfitPlots.yml
    if [ $flavor = "MuMu" ]; then
      sed -i "s/#CHANNEL#/#mu#mu channel/" postfitPlots.yml
    elif [ $flavor = "ElEl" ]; then
      sed -i "s/#CHANNEL#/ee channel/" postfitPlots.yml
    else
      sed -i "s/#CHANNEL#/#mue channel/" postfitPlots.yml
    fi

    cp postfitPlots.yml postfitPlots_${signal}_${flavor}.yml

    ../../../plotIt/plotIt -o ${output} -- ZA_plotter_all_shapes_postfit.yml

    rm postfitPlots.yml
    rm MCFiles_shapes_postfit.yml
    rm centralConfig_shapes_postfit.yml
  done
done
