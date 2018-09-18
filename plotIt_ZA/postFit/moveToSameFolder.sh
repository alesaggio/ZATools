#!/usr/bin/env bash

mass_points="MH-800_MA-200 MH-1000_MA-200 MH-800_MA-50 MH-500_MA-400 MH-800_MA-100 MH-650_MA-50 MH-250_MA-50 MH-1000_MA-50 MH-500_MA-50 MH-800_MA-400 MH-500_MA-300 MH-300_MA-100 MH-500_MA-200 MH-250_MA-100 MH-1000_MA-500 MH-300_MA-50 MH-800_MA-700 MH-200_MA-100 MH-200_MA-50 MH-300_MA-200 MH-500_MA-100"

flavors="MuMu ElEl MuEl"

extensions="pdf png"

plotDate=`date +%F`
plotDir=postFitPlots/allPlots_${plotDate}

if [ ! -d ${plotDir} ]; then
  mkdir -p ${plotDir}
fi

for flavor in $flavors; do
  for mass_point in $mass_points; do
    for ext in $extensions; do
      file=`find postFitPlots/$mass_point/$flavor -name "rho_steps."$ext`
      fileLog=`find postFitPlots/$mass_point/$flavor -name "rho_steps_logy."$ext`
      arrFILE=(${file//./ })
      arrFILElog=(${fileLog//./ })
      newFile=${arrFILE[0]}'_'${mass_point}'_'${flavor}'.'${arrFILE[1]}
      newFileLog=${arrFILElog[0]}'_'${mass_point}'_'${flavor}'.'${arrFILElog[1]}
      cp -r ./$file ./$newFile
      cp -r ./$fileLog ./$newFileLog
      mv $newFile ${plotDir}
      mv $newFileLog ${plotDir}
    done
  done
done
