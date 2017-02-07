library("zoo")
library("forecast")

predict_pay_count <- function(id, daytype, time)
{
  source_path = paste("./data/dataset/dataset/holiday_arima/", toString(id), "_", toString(daytype), sep="")
  pay_count <- read.csv(source_path)
  pay_count_ts <- ts(pay_count, start = 1)
  
  model = auto.arima(pay_count_ts)
  pay_forecast <- forecast.Arima(model, h = time, level = c(99.5))
  print('end')
  real_pay = pay_forecast$mean
  
  return(real_pay)
}

counts_frame <- data.frame()

id = 67


daytype_time_df = read.csv("./data/dataset/dataset/holiday_arima/daytype_time.txt")
pred_vec = vector()
for(daytype in 1:5)
{
  temp <- daytype_time_df[daytype_time_df$daytype==daytype,]['count']
  if(nrow(temp) == 1)
  {
    
    preds = predict_pay_count(id, daytype, temp$count)
    print(daytype)
    for (p in preds)
      pred_vec <- c(pred_vec, p)
  }
}

#print(pred_vec)

counts_frame <- rbind(counts_frame, counts)
print(counts_frame)