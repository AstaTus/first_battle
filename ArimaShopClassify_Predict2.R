
library("zoo")
library("forecast")

predict_pay_count <- function(pay_count)
{
  #print(pay_count)
  pay_count_ts <- ts(pay_count, start = 1, frequency = 7)
  
  model = auto.arima(pay_count_ts)
  pay_forecast <- forecast.Arima(model, h = 14, level = c(99.5))
  real_pay = pay_forecast$mean
  #print(real_pay)
  return(real_pay)
}

pay_counts <- read.csv("./data/dataset/dataset/shop_classify/check/predict/preprocess_data.txt", sep="\t", header = TRUE)
pay_counts <- pay_counts[2:21]
print(as.vector(pay_counts[1,],mode = "numeric"))
counts_frame <- data.frame()
pay_counts[]
for(id in 1:2000)
{
  print(id)
  #print(as.vector(pay_counts[id,],mode = "numeric"))
  counts = predict_pay_count(as.vector(pay_counts[id,],mode = "numeric"))
  #print(counts)
  counts_frame <- rbind(counts_frame, counts)
  
}

colnames(counts_frame) <- c(0:13)


write.table(counts_frame, "./data/dataset/dataset/shop_classify/check/predict/arima_prediction.txt",sep="\t")


