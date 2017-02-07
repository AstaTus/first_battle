library("zoo")
library("forecast")

predict_pay_count <- function(id, daytype, time)
{
  source_path = paste("./data/dataset/dataset/holiday_arima/", toString(id), "_", toString(daytype), sep="")
  pay_count <- read.csv(source_path)
  pay_count_ts <- ts(pay_count, start = 1)
  
  model = auto.arima(pay_count_ts)
  pay_forecast <- forecast.Arima(model, h = time, level = c(99.5))
  real_pay = pay_forecast$mean
  
  return(real_pay)
}

counts_frame <- data.frame()



daytype_time_df = read.csv("./data/dataset/dataset/holiday_arima/daytype_time.txt")

for(id in 1:2000)
{
  print(id)
  pred_vec = vector()
  for(daytype in 1:5)
  {
    temp <- daytype_time_df[daytype_time_df$daytype==daytype,]['count']
    if(nrow(temp) == 1)
    {
      preds = predict_pay_count(id, daytype, temp$count)
      for (p in preds)
        pred_vec <- c(pred_vec, p)
    }
  }
  
  counts_frame <- rbind(counts_frame, pred_vec)
}

write.csv(counts_frame, "./data/dataset/dataset/holiday_arima/result")
counts_frame
