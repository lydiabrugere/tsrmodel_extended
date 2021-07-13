## Predicting tree species richness with artificial neural networks and random forests
==============================

This repository contains the source codes for data processes and model development for the following article:  

*Brugere, L., Kwon, Y., Frazier, A. E., Kedron, P. 2021. Predicting tree species richness with artificial neural networks and random forests. Environmental Modeling and Software (In Review).*

This is also chapter 2 and chapter 3 of Lydia Brugere's PhD dissertation

### Project Organization
------------
This repo is organized according to the modeling workflow as illustrated below ![flowchart](https://github.com/lydiabrugere/tsrmodel_extended/blob/main/Supplementary_Data/Model_Workflow_Chart.png)

> `Environmental_Covariates_Processing`: The python executables extract all the 20 environmental covariates used in this study from their orignal format and resolution to the 20 km by 20 km grid system; The Jupyter notebook `random_forest_permutation_importance ` computes permutation importances fitted to the trained random forest model.  
> `Landscape_Metrics_Processing`: Process a total of 50 different landscape metrics from 2016 NLCD raster for continental U.S.
> `TSR_Outcome_Variable_Processing`: The SQL parse the FIA databases to calculate TSR in FIA plot level and then compile it to the 20 km by 20 km grid system; The Jupyter notebook `target_variable_eda.ipynb` calculate the summary statistics of the TSR and plot the frequency and density distribution.  
> `Model_Development_Evaluation`: Each jupyter notebook contains model training, hyperparameter tuning, validation and testing as the file name implies. `Model_Results_Comparison` inside this folder are scripts for model results and residuals analysis.   
> `Supplementary_Data`: contains the 20 km by 20 km grid system used in this study.  

### Model Results
![results](https://github.com/lydiabrugere/tsrmodel_extended/blob/main/Supplementary_Data/Stage1_Result.png)

### Tree Species Occurrence Data Sources
------------
FIA database (version 1.8.0.00) for the continental United States from the [FIA DataMart](https://apps.fs.usda.gov/fia/datamart/). The 20 km by 20 km grid system (a total of 20,251 grids) over the entire continental United States can be found [here](https://github.com/lydiabrugere/tsrmodel/blob/master/Supplementary_Data/Employed_Grid_System_ProjectionNAD83.zip).

### Environmental Covariates Data Sources
------------
A total of 75 variables were extracted from open source raster and vector data. See Table below: ![covariates](https://github.com/lydiabrugere/tsrmodel_extended/blob/main/Supplementary_Data/Environmental_Covariates.png)


