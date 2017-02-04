library("zoo")
library("forecast")

id = 968
source_path = paste("./data/dataset/dataset/arima/", toString(id), sep="")
pay_count <- read.csv(source_path)
pay_count_ts <- ts(pay_count, start = 1, frequency = 7)
plot.ts(pay_count_ts)

pay_count_log = pay_count_ts
#pay_count_log <- log(pay_count_ts)
plot.ts(pay_count_log)
pay_count_diff1 <- diff(pay_count_log, differences = 1)
plot.ts(pay_count_diff1)
pay_count_log
#acf(pay_count_diff1, lag.max = 56)
#acf(pay_count_diff1, lag.max = 56, plot = FALSE)

#pacf(pay_count_diff1, lag.max = 56)
#pacf(pay_count_diff1, lag.max = 56, plot = FALSE)

model = auto.arima(pay_count_log, trace = T)

#pay_arima <- arima(pay_count_log, order=c(2,1,2), seasonal = list(order = c(0, 0, 1), period = 7), method = "ML")
pay_forecast <- forecast.Arima(model, h = 14, level = c(99.5))


plot.forecast(pay_forecast)
#real_pay = exp(pay_forecast$mean)
real_pay = pay_forecast$mean
target_path = paste(source_path, "_result", sep = "")
write.csv(real_pay, target_path)
