
library("zoo")
library("forecast")

predict_pay_count <- function(id)
{
  source_path = paste("./data/dataset/dataset/arima/", toString(id), sep="")
  pay_count <- read.csv(source_path)
  pay_count_ts <- ts(pay_count, start = 1, frequency = 7)
  
  model = auto.arima(pay_count_ts)
  pay_forecast <- forecast.Arima(model, h = 14, level = c(99.5))
  real_pay = pay_forecast$mean
  
  return(real_pay)
}

counts_frame <- data.frame()
for(id in 1:2000)
{
  counts = predict_pay_count(id)
  counts_frame <- rbind(counts_frame, counts)
  
}

colnames(counts_frame) <- c(1:14)


write.csv(counts_frame, "./data/dataset/dataset/arima/result")


