
library("zoo")
library("forecast")

predict_pay_count <- function(pay_count, level)
{
  #print(pay_count)
  pay_count_ts <- ts(pay_count, start = 1, frequency = 7)
  
  model = auto.arima(pay_count_ts)
  pay_forecast <- forecast.Arima(model, h = 7, level = c(level))
  real_pay = pay_forecast$mean
  #print(real_pay)
  return(real_pay)
}

pay_counts <- read.csv("./data/dataset/dataset/shop_classify/check/train/real_train_data.txt", sep="\t", header = TRUE)
pay_counts <- pay_counts[2:21]
print(as.vector(pay_counts[1,],mode = "numeric"))
counts_frame <- data.frame()
level = 90 

for(id in 1:2000)
{
  print(id)
  #print(as.vector(pay_counts[id,],mode = "numeric"))
  counts = predict_pay_count(as.vector(pay_counts[id,],mode = "numeric"), level)
  #print(counts)
  counts_frame <- rbind(counts_frame, counts)
  
}

colnames(counts_frame) <- c(0:6)

save_path = paste("./data/dataset/dataset/shop_classify/check/train/", toString(level), sep="")
save_path = paste(save_path, '_arima_prediction.txt', sep="")
write.table(counts_frame, save_path, sep="\t")
