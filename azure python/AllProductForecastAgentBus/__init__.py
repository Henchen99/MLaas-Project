import logging

import azure.functions as func

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.model_selection import ShuffleSplit
import sklearn.model_selection as curves
from time import time
import os
from sklearn.metrics import mean_absolute_percentage_error as mape, mean_squared_error as mse
import io

from azure.storage.queue import QueueMessage
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient


def main(predSamp: func.ServiceBusMessage, allProd: func.Out[str]) -> None:
    logging.info('Python queue trigger function processed a queue item: %s',
                predSamp.get_body().decode('utf-8'))
    
    
    logging.info("****THIS HAS TRIGGERD AFTER PREDICTION SAMPLE PROCESSING****")

    # Define your connection string and container name
    connection_string = "DefaultEndpointsProtocol=https;AccountName=sftpagentgroupa4ac;AccountKey=4V95xpvoK2THUxuxlBqFDfLstMO/UbTG3Ot8jYuH559fYPXe+DVujiLtcatxyI00NU/2rbL4Crgo+AStDfvRaw==;EndpointSuffix=core.windows.net"
    container_name = "ff-process-stage2"

    # Create a BlobServiceClient object to interact with the Blob Storage service
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Create an empty list to store blobs
    blob_list = []
    dataframes = []

    # list blobs sorted by creation time
    blobs = blob_service_client.get_container_client(container_name).list_blobs()
    blobs = sorted(blobs, key=lambda b: b.creation_time, reverse=True)
    # Append the blobs to the list
    for blob in blobs:
        blob_list.append(blob)
    # logging.info(blob_list)

    for blob in blob_list:
        blob_client = blob_service_client.get_blob_client(container_name, blob.name)
        logging.info("******BLOB NAME******")
        logging.info(blob.name)

        download_stream = blob_client.download_blob()

        data = download_stream.readall()

        # Convert bytes to file-like object
        data_file = io.BytesIO(data)

        # Read the CSV using the file-like object and append to the list
        df = pd.read_excel(data_file)

        dataframes.append(df)
    

    # Load the transformed dataset
    tsal_inv_df = dataframes[0]
    test_df = dataframes[1]

    logging.info("*****ALL_PROD_tsal_inv_df*****")
    logging.info(tsal_inv_df)
    logging.info("*****ALL_PROD_test_df*****")
    logging.info(test_df)

    tsal_inv_df += 1
    test_df += 1

    logging.info("*****ALL_PROD_tsal_inv_df*****")
    logging.info(tsal_inv_df)
    logging.info("*****ALL_PROD_test_df*****")
    logging.info(test_df)

    # # Load all the dataset
    # tsal_inv_df = pd.read_excel("cleaned_sal_inv_data.xlsx")
    # test_df = pd.read_excel("test_data.xlsx")
    # nov_pred_df = pd.read_excel("nov_pred_df.xlsx")
    # dec_pred_df = pd.read_excel("dec_pred_df.xlsx")
    # jan_pred_df = pd.read_excel("jan_pred_df.xlsx")

    # # dropping certain columns to make all dataset consistent throughout
    # nov_pred_df.drop(["Unnamed: 0"], inplace=True, axis=1)
    # dec_pred_df.drop(["Unnamed: 0"], inplace=True, axis=1)
    # jan_pred_df.drop(["Unnamed: 0"], inplace=True, axis=1)
    # tsal_inv_df.drop(["Total inv", 'Product Title', 'UPC', 'Model No'], inplace=True, axis=1)
    # test_df.drop(['Product Title', 'UPC', 'Model No'], inplace=True, axis=1)

    # tsal_inv_df.sort_values(by="Date", inplace=True, ignore_index=True)
    # test_df.sort_values(by="Date", inplace=True, ignore_index=True)
    # nov_pred_df.sort_values(by="Date", inplace=True, ignore_index=True)
    # dec_pred_df.sort_values(by="Date", inplace=True, ignore_index=True)
    # jan_pred_df.sort_values(by="Date", inplace=True, ignore_index=True)

    # def time_feature (dataset):

    #     date_features = {
    #         "dayofweek": "dayofweek",
    #         "weekofyear": "weekofyear",
    #         "month": "month",
    #         "quarter": "quarter",
    #         "year": "year",
    #         "day": "day",
    #         "week": "week",
    #         "dayofyear": "dayofyear",
    #         "is_month_start": "is_month_start",
    #         "is_month_end": "is_month_end",
    #     }

    #     for date_feat_name, date_feat_func in date_features.items():
    #         if date_feat_name in dataset.columns:
    #             dataset[date_feat_name] = dataset[date_feat_name].astype("int16")
    #         else:
    #             dataset[date_feat_name] = getattr(
    #                 dataset["Date"].dt, date_feat_func
    #             ).astype("int16")
    #     return dataset

    # tsal_inv_df = time_feature(tsal_inv_df)
    # test_df = time_feature(test_df)
    # nov_pred_df = time_feature(nov_pred_df)
    # dec_pred_df = time_feature(dec_pred_df)
    # jan_pred_df = time_feature(jan_pred_df)

    # tsal_inv_df = tsal_inv_df[tsal_inv_df["Ordered Units"] > 0]
    # test_df = test_df[test_df["Ordered Units"] > 0]

    # tsal_inv_df = tsal_inv_df[tsal_inv_df["Ordered Units"] < 2500]
    # test_df = test_df[test_df["Ordered Units"] < 2500]

    # tsal_inv_df = tsal_inv_df[
    #     (tsal_inv_df["Date"] != "2022-04-13") & (tsal_inv_df["Ordered Units"] < 2000)
    # ]

    # nov_pred_df.reset_index(inplace=True, drop=True)
    # dec_pred_df.reset_index(inplace=True, drop=True)
    # jan_pred_df.reset_index(inplace=True, drop=True)
    # test_df.reset_index(inplace=True, drop=True)
    # tsal_inv_df.reset_index(inplace=True, drop=True)

    # """## Clean, encode and transform all the data features into data types which are interpretable by the machine learning model

    # """

    # from rdt import HyperTransformer

    # ht = HyperTransformer()
    # ht.detect_initial_config(data=tsal_inv_df)

    # # import and create new transformer objects
    # from rdt.transformers.categorical import FrequencyEncoder

    # categorical_transformer = FrequencyEncoder()

    # ht.update_transformers(
    #     column_name_to_transformer={
    #         "Subcategory (Sales Rank)": categorical_transformer,
    #     }
    # )

    # ht.remove_transformers(column_names=["Date"])

    # ht.get_config()

    # ht.fit(tsal_inv_df)

    # transformed_train_df = ht.transform(tsal_inv_df)
    # transformed_test_df = ht.transform(test_df)
    # transformed_nov_pred_df = ht.transform(nov_pred_df)
    # transformed_dec_pred_df = ht.transform(dec_pred_df)
    # transformed_jan_pred_df = ht.transform(jan_pred_df)

    # def rename (dataset):

    #     dataset.rename(
    #         columns={
    #             "ASIN.value": "ASIN",
    #             "Shipped COGS.value": "Shipped_COGS",
    #             "Shipped COGS - % of Total.value": "Shipped_COGS_Total_Value",
    #             "Shipped COGS - Prior Period.value": "Shipped_COGS_Prior_Value",
    #             "Shipped COGS - Last Year.value": "Shipped_COGS_Last_Year",
    #             "Shipped Units.value": "Shipped_Units",
    #             "Shipped Units - % of Total.value": "Shipped_Units_Total_Value",
    #             "Shipped Units - Prior Period.value": "Shipped_Units_Prior_Value",
    #             "Shipped Units - Last Year.value": "Shipped_Units_Last_Year",
    #             "Ordered Units.value": "Ordered_Units",
    #             "Ordered Units - % of Total.value": "Ordered_Units_Total_Value",
    #             "Ordered Units - Prior Period.value": "Ordered_Units_Prior_Value",
    #             "Ordered Units - Last Year.value": "Ordered_Units_Last_Year",
    #             "Customer Returns.value": "Return",
    #             "Free Replacements.value": "Free_Replacement",
    #             "Subcategory (Sales Rank).value": "Sales_Rank",
    #             "Average Sales Price.value": "Average_Sales_Price",
    #             "Average Sales Price - Prior Period.value": "Average_Sales_Price_Prior_Value",
    #             "Glance Views.value": "Glance_Views",
    #             "Change in Glance View - Prior Period.value": "Glance_Views_Prior_Value",
    #             "Change in GV Last Year.value": "Glance_Views_Last_Year",
    #             "Conversion Rate.value": "Conversion_Rate",
    #             "Rep OOS.value": "Rep",
    #             "Rep OOS - % of Total.value": "Rep_Total_Value",
    #             "Rep OOS - Prior Period.value": "Rep_Prior_Value",
    #             "LBB (Price).value": "LBB",
    #             "AMZ Inv.value": "AMZ_inv",
    #             "Furinno Inv.value": "Furinno_inv",
    #             "dayofweek.value": "dayofweek",
    #             "weekofyear.value": "weekofyear",
    #             "month.value": "month",
    #             "quarter.value": "quarter",
    #             "year.value": "year",
    #             "day.value": "day",
    #             "week.value": "week",
    #             "dayofyear.value": "dayofyear",
    #             "is_month_start.value": "is_month_start",
    #             "is_month_end.value": "is_month_end",
    #         },
    #         inplace=True,
    #     )
    #     return dataset

    # transformed_train_df = rename(transformed_train_df)
    # transformed_test_df = rename(transformed_test_df)
    # transformed_nov_pred_df = rename(transformed_nov_pred_df)
    # transformed_dec_pred_df = rename(transformed_dec_pred_df)
    # transformed_jan_pred_df = rename(transformed_jan_pred_df)

    # ytrain = transformed_train_df["Ordered_Units"].copy()
    # ytest = transformed_test_df["Ordered_Units"].copy()

    # transformed_train_df.drop(["Date", "Ordered_Units"], axis=1, inplace=True)
    # transformed_test_df.drop(["Date", "Ordered_Units"], axis=1, inplace=True)
    # transformed_nov_pred_df.drop(["Date", "Ordered_Units"], axis=1, inplace=True)
    # transformed_dec_pred_df.drop(["Date", "Ordered_Units"], axis=1, inplace=True)
    # transformed_jan_pred_df.drop(["Date", "Ordered_Units"], axis=1, inplace=True)

    # """## Lightgbm base model to test predominantly the performance of the data structures efficiency

    # """

    # params_p = {
    #     "learning_rate": 0.19483980858626945,
    #     "max_depth": 12,
    #     "bagging_fraction": 0.2,
    #     "feature_fraction": 0.4,
    #     "lambda_l2": 100,
    #     "lambda_l1": 75,
    #     "reg_alpha": 0.2458769456607237,
    #     "reg_lambda": 9.408720654061234,
    #     "min_gain_to_split": 0.0015099426408213823,
    #     "num_leaves": 2760,
    #     "min_data_in_leaf": 200,
    # }


    # m_lgb_p = lgb.LGBMRegressor(objective="poisson", **params_p)
    # m_lgb_p.fit(
    #     transformed_train_df,
    #     ytrain,
    #     eval_set=[(transformed_test_df, ytest)],
    #     eval_metric="rmse",
    #     early_stopping_rounds=100,
    # )

    # # Fit the model to the training data
    # m_lgb_p.fit(transformed_train_df, ytrain)

    # """## Cross-validation to double verify the model performance reliability and credibility

    # """

    # def my_rmse(x, y):
    #     return np.round(np.sqrt(mse(x, y)), 4)

    # # creating a function to test the MAPE of the model
    # def my_mape(actual, forecast):
    #     return np.round(np.mean(np.abs((actual - forecast) / actual)) * 100, 4)
    # lgb_pred_p = m_lgb_p.predict(transformed_test_df)

    # nov_prediction = m_lgb_p.predict(transformed_nov_pred_df)
    # dec_prediction = m_lgb_p.predict(transformed_dec_pred_df)
    # jan_prediction = m_lgb_p.predict(transformed_jan_pred_df)

    # transformed_nov_pred_df["Forecast"] = nov_prediction
    # transformed_dec_pred_df["Forecast"] = dec_prediction
    # transformed_jan_pred_df["Forecast"] = jan_prediction

    # # replacing certain column with another dataset 
    # def replace(dataset, column, new_dataset):
    #     dataset[column] = new_dataset[column]
    #     return dataset

    # nov_pred_df = replace(transformed_dec_pred_df, "ASIN", dec_pred_df)

    # transformed_nov_pred_df.to_excel("forecast_nov.xlsx")
    # transformed_dec_pred_df.to_excel("forecast_dec.xlsx")
    # transformed_jan_pred_df.to_excel("forecast_jan.xlsx")

    # """## Using Optuna framework to fine tune the Lightgbm hyperparameter

    # """

    # import optuna
    # from sklearn.metrics import log_loss
    # from sklearn.model_selection import StratifiedKFold
    # from optuna.integration import LightGBMPruningCallback

    # def objective(trial, X, y):
    #     param_grid = {
    #         "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
    #         "num_leaves": trial.suggest_int("num_leaves", 20, 3000, step=20),
    #         "max_depth": trial.suggest_int("max_depth", 3, 12),
    #         "min_data_in_leaf": trial.suggest_int("min_data_in_leaf", 200, 10000, step=100),
    #         "lambda_l1": trial.suggest_int("lambda_l1", 0, 100, step=5),
    #         "lambda_l2": trial.suggest_int("lambda_l2", 0, 100, step=5),
    #         "reg_alpha": trial.suggest_loguniform("reg_alpha", 1e-3, 10.0),
    #         "reg_lambda": trial.suggest_loguniform("reg_lambda", 1e-3, 10.0),
    #         "min_gain_to_split": trial.suggest_float("min_gain_to_split", 0, 15),
    #         "bagging_fraction": trial.suggest_float(
    #             "bagging_fraction", 0.2, 0.95, step=0.1
    #         ),
    #         "feature_fraction": trial.suggest_float(
    #             "feature_fraction", 0.2, 0.95, step=0.1
    #         ),
    #     }

    #     cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=1121218)

    #     cv_scores = np.empty(5)
    #     for idx, (train_idx, test_idx) in enumerate(cv.split(X, y)):
    #         X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    #         y_train, y_test = y[train_idx], y[test_idx]

    #         model = lgb.LGBMRegressor(objective="poisson", **param_grid)
    #         model.fit(
    #             X_train,
    #             y_train,
    #             eval_set=[(X_test, y_test)],
    #             eval_metric="rmse",
    #             early_stopping_rounds=100,
    #             callbacks=[
    #                 LightGBMPruningCallback(trial, "rmse")
    #             ],  # Add a pruning callback
    #         )
    #         preds = model.predict(X_test)
    #         cv_scores[idx] = my_rmse(y_test, preds)

    #     return np.mean(cv_scores)

    # study = optuna.create_study(direction="minimize", study_name="LGBM Classifier")
    # func = lambda trial: objective(trial, transformed_train_df, ytrain)
    # study.optimize(func, n_trials=20)

    # transformed_test_df

    passing_dataframes = [tsal_inv_df, test_df]

    # Define your connection string and container name
    connection_string = "DefaultEndpointsProtocol=https;AccountName=sftpagentgroupa4ac;AccountKey=4V95xpvoK2THUxuxlBqFDfLstMO/UbTG3Ot8jYuH559fYPXe+DVujiLtcatxyI00NU/2rbL4Crgo+AStDfvRaw==;EndpointSuffix=core.windows.net"
    container_name = "sftp-upload-data"
    # container_name = "furinno-forecast-upload-data"

    # Create a BlobServiceClient object to interact with the Blob Storage service
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    for index, df in enumerate(passing_dataframes):
        
        # Get a reference to the container
        container_client = blob_service_client.get_container_client(container_name)
        
        # Create a BytesIO object to hold the Excel data
        excel_data = io.BytesIO()
        
        # Write the DataFrame to the BytesIO object as an Excel file
        df.to_excel(excel_data, index=False)
        excel_data.seek(0)  # Reset the position of the BytesIO object to the beginning
        
        # Create a BlobClient object to represent the Excel file you want to upload
        filename = f"df{index + 1}.xlsx"
        blob_client = container_client.get_blob_client(filename)
        
        # Upload the file to Blob Storage
        logging.info("blob uploaded")
        blob_client.upload_blob(excel_data, overwrite=True)


    allProd.set("****THIS HAS TRIGGERD AFTER PREDICTION SAMPLE PROCESSING****")