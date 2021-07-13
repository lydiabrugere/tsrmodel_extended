library(raster)
library(dplyr)
library(landscapemetrics)
library(stringr)

getwd()
path = "./data/clipped2grid_projected/"
file.names <- dir(path, pattern =".tif")

# For a total of 1042 grids
for(i in 1:length(file.names)){
  tif <- file.names[i]
  tif_path <- paste(path, tif, sep='')
  landscape <- raster(tif_path)
  check_landscape(landscapemetrics::landscape)
  
  ########################## START: CALCULATE LANDSCAPE LEVEL METRICS
  # list all metrics at landscape level and return variable
  lsm_lanscape <- list_lsm(level = "landscape",simplify = TRUE) # 65
  
  # calculate all metrics at landscape level
  lsm_landscape_results <- calculate_lsm(landscape=landscape, what = lsm_lanscape, classes_max=length(unique(landscape)), progress = TRUE)
  
  # save results to csv
  landscape_result <- paste('./data/lsm_landscape_results/', str_sub(tif, end=-5), '.csv', sep = '')
  write.table(as.data.frame(lsm_landscape_results),file=landscape_result, quote=F,sep=",",row.names=F)
  ########################## END: CALCULATE LANDSCAPE LEVEL METRICS
}

