# Cost-of-sales forecast (Article 4, Barrick Gold Research).
# R packages and tested versions: see R_requirements.txt in this folder.
#
# Usage:
#   Rscript cost_of_sales.R [COST_CSV] [WEIGHTS_CSV] [OUTPUT_DIR]
# Defaults (relative to this script's folder):
#   COST_CSV    = data/cost_of_sales.csv
#   WEIGHTS_CSV = data/cost_of_sales_weights.csv
#   OUTPUT_DIR  = output/
#
# Expected input layout (both CSVs, one row per mine-year, "wide" quarters):
#   Miniera  - mine name (must match exactly between the two files)
#   Anno     - calendar year (e.g. 2019)
#   Q1,Q2,Q3,Q4 - quarterly values; "N/D" or empty = not available
# COST_CSV:    cost of sales per ounce sold (US$/oz), mine level, as reported in
#              Barrick's quarterly MD&A / "Mine Stats" operating tables.
# WEIGHTS_CSV: gold ounces sold in the same mine-quarter, on the same basis
#              (attributable vs 100%) as the cost per ounce. Used as weights.

library(dplyr)
library(tidyr)
library(ggplot2)
library(lubridate)
library(zoo)
library(forecast)
library(tseries)

# =====================================================================
# CONFIGURATION
# =====================================================================

get_script_dir <- function() {
  file_arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
  if (length(file_arg) == 1) return(dirname(normalizePath(sub("^--file=", "", file_arg))))
  getwd()  # interactive use: run from the cost_of_sales/ folder
}
SCRIPT_DIR <- get_script_dir()
cli_args   <- commandArgs(trailingOnly = TRUE)

COST_CSV_PATH    <- if (length(cli_args) >= 1) cli_args[1] else file.path(SCRIPT_DIR, "data", "cost_of_sales.csv")
WEIGHTS_CSV_PATH <- if (length(cli_args) >= 2) cli_args[2] else file.path(SCRIPT_DIR, "data", "cost_of_sales_weights.csv")
OUTPUT_DIR       <- if (length(cli_args) >= 3) cli_args[3] else file.path(SCRIPT_DIR, "output")

# "production" (default): ounce-weighted average across mines.
# "equal": unweighted mean, kept ONLY to reproduce the run published on 8 May 2026.
WEIGHTING <- "production"

# Out-of-sample settings (Chunk 6)
H_TEST    <- 12  # single hold-out length (quarters)
H_CV      <- 4   # rolling-origin horizon (quarters)
MIN_TRAIN <- 16  # first rolling-origin training window (quarters)

# =====================================================================
# CHUNK 1: DATA LOADING & PREPARATION
# =====================================================================

read_wide_quarterly <- function(path, what) {
  if (!file.exists(path)) {
    stop(sprintf(paste0(
      "%s file not found: %s\n",
      "Expected a CSV with columns Miniera, Anno, Q1, Q2, Q3, Q4 (see header of this script\n",
      "and the 'Data needed to reproduce' section of the README). Pass the path as a\n",
      "command-line argument or place the file at the default location."), what, path),
      call. = FALSE)
  }
  df <- read.csv(path, stringsAsFactors = FALSE, check.names = FALSE)
  missing_cols <- setdiff(c("Miniera", "Anno", "Q1", "Q2", "Q3", "Q4"), names(df))
  if (length(missing_cols) > 0) {
    stop(sprintf("%s file %s is missing columns: %s", what, path,
                 paste(missing_cols, collapse = ", ")), call. = FALSE)
  }
  df %>%
    pivot_longer(
      cols = c(Q1, Q2, Q3, Q4),
      names_to = "Q", values_to = "Value",
      values_transform = list(Value = as.character)
    ) %>%
    mutate(
      Value = trimws(Value),
      Value = ifelse(Value == "N/D" | Value == "", NA, Value),
      Value = as.numeric(Value),
      Quarter_Str = paste(Anno, Q),
      YearQtr = as.yearqtr(Quarter_Str, format = "%Y Q%q"),
      Date = as.Date(YearQtr)
    ) %>%
    filter(!is.na(Value))
}

long_df <- read_wide_quarterly(COST_CSV_PATH, "Cost-of-sales") %>%
  filter(Date >= as.Date("2017-01-01")) %>%
  arrange(Miniera, Date)


# =====================================================================
# CHUNK 2: MASTER CHAIN CREATION (LOG-SPACE)
# =====================================================================

# The mine panel is unbalanced (mines enter/leave the sample and have
# different sizes). A simple mean gives a small mine the same weight as a
# large one, so the "company" cost per ounce jumps whenever the mix changes.
# The variable is a cost per ounce SOLD, so the consistent aggregate is the
# ounce-weighted mean:  sum_i(CoS/oz_i * oz_i) / sum_i(oz_i)  = total cost of
# sales / total ounces sold for the mines in the panel that quarter.
# Weighting reduces, but does not remove, composition breaks when a mine
# enters or exits the panel.
if (WEIGHTING == "production") {
  weights_long <- read_wide_quarterly(WEIGHTS_CSV_PATH, "Ounces-sold weights") %>%
    select(Miniera, Date, Weight = Value)
  long_w <- long_df %>% left_join(weights_long, by = c("Miniera", "Date"))
  bad_w <- long_w %>% filter(is.na(Weight) | Weight <= 0)
  if (nrow(bad_w) > 0) {
    warning(sprintf(
      "%d mine-quarters have a cost but no positive ounces-sold weight; they are excluded from the weighted average: %s",
      nrow(bad_w), paste(unique(paste(bad_w$Miniera, bad_w$YearQtr)), collapse = "; ")))
  }
  avg_hist <- long_w %>%
    filter(!is.na(Weight), Weight > 0) %>%
    group_by(Date, YearQtr) %>%
    summarise(Avg_Value = weighted.mean(Value, Weight), N_Mines = n(), .groups = "drop")
} else if (WEIGHTING == "equal") {
  warning("WEIGHTING = 'equal': unweighted mean across an unbalanced panel (legacy, published run only).")
  avg_hist <- long_df %>%
    group_by(Date, YearQtr) %>%
    summarise(Avg_Value = mean(Value, na.rm = TRUE), N_Mines = n(), .groups = "drop")
} else {
  stop("WEIGHTING must be 'production' or 'equal'.", call. = FALSE)
}
avg_hist <- avg_hist %>%
  mutate(Log_Value = log(Avg_Value)) %>%
  arrange(Date)

# ts() assumes consecutive quarters: fail loudly on gaps.
if (any(round(diff(as.numeric(avg_hist$YearQtr)) * 4) != 1)) {
  stop("The aggregated cost series has missing quarters; fill the input data before fitting.", call. = FALSE)
}

start_year <- as.numeric(format(min(avg_hist$Date), "%Y"))
start_qtr  <- (as.numeric(format(min(avg_hist$Date), "%m")) - 1) / 3 + 1

ts_log <- ts(avg_hist$Log_Value, 
             start = c(start_year, start_qtr), 
             frequency = 4)


# =====================================================================
# CHUNK 3: HISTORICAL DATA PLOTTING (2019 ONWARDS)
# =====================================================================

storico_2020 <- long_df %>%
  filter(Date >= as.Date("2019-01-01"))

# Linear Scale Plot
p_storico_lin <- ggplot(storico_2020, aes(x = Date, y = Value, color = Miniera)) +
  geom_line(size = 1) +
  labs(title = "Historical Time Series by Mine",
       subtitle = "Linear Scale", y = "Cost of Sales", x = "Date") +
  theme_bw() + theme(legend.position = "right")
print(p_storico_lin)

# Logarithmic Scale Plot
p_storico_log <- ggplot(storico_2020, aes(x = Date, y = Value, color = Miniera)) +
  geom_line(size = 1) + scale_y_log10() +  
  labs(title = "Historical Time Series by Mine ",
       subtitle = "Logarithmic Scale", y = "Cost of Sales (Log Scale)", x = "Date") +
  theme_bw() + theme(legend.position = "right")
print(p_storico_log)


# =====================================================================
# CHUNK 4: ARIMA PRE-MODELING & STATIONARITY TESTS
# =====================================================================

cat("\n--- ADF TEST (Unit Root) ---\n")
tryCatch(print(adf.test(ts_log, alternative = "stationary")), 
         error = function(e) cat("ADF Error:", e$message, "\n"))

cat("\n--- KPSS TEST (Trend-Stationary) ---\n")
tryCatch(print(kpss.test(ts_log)), 
         error = function(e) cat("KPSS Error:", e$message, "\n"))


# =====================================================================
# CHUNK 5: ARIMA MODEL FITTING & DIAGNOSTICS
# =====================================================================

# Single model-selection procedure, used for the final forecast AND for every
# validation window, so the out-of-sample test measures the procedure that
# actually produces the forecast.
fit_cos_model <- function(y) {
  auto.arima(y, seasonal = TRUE, stepwise = FALSE, approximation = FALSE)
}

cat("\n--- FITTING SARIMA MODEL ---\n")
fit <- fit_cos_model(ts_log)
print(fit)

# Inverse Roots Plot
autoplot(fit) + 
  ggtitle("Inverse AR and MA Roots of the Chosen SARIMA Model") + theme_minimal()

cat("\n--- RESIDUAL DIAGNOSTICS (Ljung-Box Test) ---\n")
checkresiduals(fit)

cat("\n--- NORMALITY TEST (Shapiro-Wilk) ---\n")
tryCatch(print(shapiro.test(fit$residuals)),
         error = function(e) cat("Shapiro Error:", e$message, "\n"))


# =====================================================================
# CHUNK 6: OUT-OF-SAMPLE VALIDATION
# =====================================================================

h_test <- H_TEST
n_total <- length(ts_log)

# (a) Single hold-out: auto.arima re-run on the training window only.
train_set <- head(ts_log, n_total - h_test)
test_set  <- tail(ts_log, h_test)

fit_train <- fit_cos_model(train_set)
train_label <- as.character(fit_train)

arima_forecast <- forecast(fit_train, h = h_test)
naive_forecast <- naive(train_set, h = h_test)

cat("\n--- HOLD-OUT ACCURACY:", train_label, "(auto.arima on training window) ---\n")
print(accuracy(arima_forecast, test_set))
cat("\n--- HOLD-OUT ACCURACY: NAIVE MODEL (Benchmark) ---\n")
print(accuracy(naive_forecast, test_set))

autoplot(arima_forecast) +
  autolayer(test_set, series = "Actual Data (Test Set)", color = "red") +
  ggtitle(paste("Out-of-Sample Validation:", train_label, "vs Actual Data")) +
  ylab("Log Values") + theme_minimal()

# (b) Rolling origin (expanding window): auto.arima is re-selected and
# re-estimated at every forecast origin, exactly as for the final forecast.
cat("\n--- ROLLING-ORIGIN CV (auto.arima refit at each origin) ---\n")
e_arima <- tsCV(ts_log, function(y, h) forecast(fit_cos_model(y), h = h),
                h = H_CV, initial = MIN_TRAIN)
e_naive <- tsCV(ts_log, function(y, h) naive(y, h = h),
                h = H_CV, initial = MIN_TRAIN)
cv_table <- data.frame(
  Horizon     = seq_len(H_CV),
  RMSE_ARIMA  = sqrt(colMeans(as.matrix(e_arima)^2, na.rm = TRUE)),
  RMSE_Naive  = sqrt(colMeans(as.matrix(e_naive)^2, na.rm = TRUE)),
  N_Forecasts = colSums(!is.na(as.matrix(e_arima)))
)
print(cv_table, row.names = FALSE)


# =====================================================================
# CHUNK 7: GLOBAL MASTER CHAIN FORECAST GENERATION
# =====================================================================

fc_obj <- forecast(fit, h = 20, level = c(95)) 

fc_global_log <- data.frame(
  Date = as.Date(as.yearqtr(time(fc_obj$mean))),
  Log_Value = as.numeric(fc_obj$mean), 
  Log_Lower = as.numeric(fc_obj$lower),
  Log_Upper = as.numeric(fc_obj$upper)
) %>%
  mutate(Log_CI_Radius = (Log_Upper - Log_Lower) / 2)

global_chain_log <- bind_rows(
  avg_hist %>% select(Date, Log_Value),
  fc_global_log %>% select(Date, Log_Value)
) %>%
  arrange(Date) %>%
  mutate(Delta_Log_Global = Log_Value - lag(Log_Value, default = first(Log_Value)))


# =====================================================================
# CHUNK 8: INDIVIDUAL MINE FORECAST COMPUTATION (WITH BETA)
# =====================================================================

mine_anchors <- long_df %>%
  group_by(Miniera) %>%
  slice_max(Date, n = 1) %>% 
  select(Miniera, Anchor_Date = Date, Anchor_Value = Value) %>%
  mutate(Anchor_Log = log(Anchor_Value))

final_forecast_list <- list()

for(m in unique(mine_anchors$Miniera)) {
  
  mine_hist <- long_df %>% filter(Miniera == m) %>% arrange(Date)
  
  log_returns_data <- mine_hist %>%
    mutate(Log_Value_Mine = log(Value)) %>%
    mutate(Delta_Log_Mine = c(NA, diff(Log_Value_Mine))) %>%
    inner_join(global_chain_log %>% 
                 mutate(Delta_Log_Global_Hist = c(NA, diff(Log_Value))) %>%
                 select(Date, Delta_Log_Global_Hist), 
               by = "Date") %>%
    filter(!is.na(Delta_Log_Mine) & !is.na(Delta_Log_Global_Hist))
  
  # Beta Calculation & Shrinkage
  if(nrow(log_returns_data) > 6) {
    sd_mine <- sd(log_returns_data$Delta_Log_Mine, na.rm = TRUE)
    sd_global <- sd(log_returns_data$Delta_Log_Global_Hist, na.rm = TRUE)
    
    if(!is.na(sd_mine) && !is.na(sd_global) && sd_global > 0.0001) {
      beta_raw <- sd_mine / sd_global
    } else {
      beta_raw <- 1.0
    }
    beta_multiplier <- (0.67 * beta_raw) + (0.33 * 1.0)
    
  } else {
    beta_multiplier <- 1.0 
  }
  
  # Beta Clamps
  if(is.na(beta_multiplier)) beta_multiplier <- 1.0
  if(beta_multiplier < 0.1) beta_multiplier <- 0.1
  if(beta_multiplier > 2.5) beta_multiplier <- 2.5
  
  # Projection
  anchor <- mine_anchors %>% filter(Miniera == m)
  
  future_deltas <- global_chain_log %>%
    filter(Date > anchor$Anchor_Date) %>%
    mutate(Miniera = m)
  
  future_data <- future_deltas %>%
    left_join(fc_global_log %>% select(Date, Log_CI_Radius), by = "Date") %>%
    mutate(
      Adjusted_Delta = Delta_Log_Global * beta_multiplier,
      Cumulative_Log_Change = cumsum(Adjusted_Delta),
      Forecast_Log = anchor$Anchor_Log + Cumulative_Log_Change,
      Mine_Log_Radius = Log_CI_Radius * beta_multiplier,
      Lower_Log = Forecast_Log - Mine_Log_Radius,
      Upper_Log = Forecast_Log + Mine_Log_Radius,
      Value = exp(Forecast_Log),
      Lower_CI = exp(Lower_Log),
      Upper_CI = exp(Upper_Log),
      Type = "Forecast"
    ) %>%
    select(Miniera, Date, Value, Lower_CI, Upper_CI, Type)
  
  final_forecast_list[[m]] <- future_data
}

final_forecast_df <- bind_rows(final_forecast_list)


# =====================================================================
# CHUNK 9: PLOTTING INDIVIDUAL FORECASTS
# =====================================================================

hist_data <- long_df %>% 
  select(Miniera, Date, Value) %>% 
  mutate(Type = "Historical", Lower_CI = NA, Upper_CI = NA)

plot_data <- bind_rows(hist_data, final_forecast_df)

max_hist_date <- max(hist_data$Date, na.rm = TRUE)
plot_end_date <- as.Date(as.yearqtr(max_hist_date) + 2)
plot_start_date <- as.Date("2020-01-01")

p <- ggplot(plot_data, aes(x = Date, y = Value)) +
  geom_ribbon(aes(ymin = Lower_CI, ymax = Upper_CI, fill = Type), alpha = 0.2) +
  geom_line(aes(color = Type), size = 1) +
  facet_wrap(~Miniera, scales = "free_y", ncol = 3) + 
  scale_color_manual(values = c("Historical" = "#525252", "Forecast" = "#e31a1c")) +
  scale_fill_manual(values = c("Historical" = NA, "Forecast" = "#e31a1c")) +
  coord_cartesian(xlim = c(plot_start_date, plot_end_date)) +
  labs(title = "Forecasts shifted (Zoom a 2 Anni)", y = "Cost of sales", x = NULL) +
  theme_bw() + theme(legend.position = "top")

print(p)


# =====================================================================
# CHUNK 10: PLOTTING GLOBAL FORECAST & PRINTING TABLES
# =====================================================================

# Individual Mine Output Table
output_table <- final_forecast_df %>%
  mutate(Quarter = as.character(as.yearqtr(Date)),
         Value = round(Value, 2), Lower_CI = round(Lower_CI, 2), Upper_CI = round(Upper_CI, 2)) %>%
  select(Miniera, Quarter, Date, Value, Lower_CI, Upper_CI)

cat("\n--- FORECAST PER MINIERA ---\n")
print(as.data.frame(output_table))

# Global Chain Output Table
global_output_table <- fc_global_log %>%
  mutate(Quarter = as.character(as.yearqtr(Date)),
         Global_Value = round(exp(Log_Value), 2), 
         Global_Lower = round(exp(Log_Lower), 2), Global_Upper = round(exp(Log_Upper), 2)) %>%
  select(Quarter, Date, Global_Value, Global_Lower, Global_Upper)

cat("\n--- FORECAST GLOBAL MASTER CHAIN (Avg Market Trend) ---\n")
print(as.data.frame(global_output_table))

# Export for ebitda_montecarlo/ebitda_mc.ipynb. Global_Value is exp(log
# forecast), i.e. the median cost of sales per oz; Log_SD is the forecast
# standard deviation in log space at each horizon (95% radius / 1.96), used
# there to draw cost shocks. Resid_SD = in-sample one-step residual s.d.
dir.create(OUTPUT_DIR, showWarnings = FALSE, recursive = TRUE)
cost_export <- fc_global_log %>%
  mutate(Quarter = as.character(as.yearqtr(Date)),
         Global_Value = exp(Log_Value),
         Global_Lower = exp(Log_Lower), Global_Upper = exp(Log_Upper),
         Log_Mean = Log_Value,
         Log_SD = Log_CI_Radius / qnorm(0.975),
         Resid_SD = sqrt(fit$sigma2),
         Model = as.character(fit),
         Weighting = WEIGHTING) %>%
  select(Quarter, Date, Global_Value, Global_Lower, Global_Upper, Log_Mean, Log_SD, Resid_SD, Model, Weighting)
write.csv(cost_export, file.path(OUTPUT_DIR, "cost_forecast_global.csv"), row.names = FALSE)
write.csv(output_table, file.path(OUTPUT_DIR, "cost_forecast_by_mine.csv"), row.names = FALSE)
cat("\nForecast tables written to", normalizePath(OUTPUT_DIR), "\n")

# Global Plot
plot_global_hist <- avg_hist %>%
  mutate(Value = exp(Log_Value), Lower_CI = NA, Upper_CI = NA, Type = "Historical") %>%
  select(Date, Value, Lower_CI, Upper_CI, Type)

plot_global_fc <- fc_global_log %>%
  mutate(Value = exp(Log_Value), Lower_CI = exp(Log_Lower), Upper_CI = exp(Log_Upper), Type = "Forecast") %>%
  select(Date, Value, Lower_CI, Upper_CI, Type)

plot_global_data <- bind_rows(plot_global_hist, plot_global_fc)

max_global_hist_date <- max(plot_global_hist$Date, na.rm = TRUE)
global_plot_end_date <- as.Date(as.yearqtr(max_global_hist_date) + 2)

p_global <- ggplot(plot_global_data, aes(x = Date, y = Value)) +
  geom_ribbon(aes(ymin = Lower_CI, ymax = Upper_CI, fill = Type), alpha = 0.2) +
  geom_line(aes(color = Type), size = 1.2) +
  scale_color_manual(values = c("Historical" = "#525252", "Forecast" = "#e31a1c")) +
  scale_fill_manual(values = c("Historical" = NA, "Forecast" = "#e31a1c")) +
  coord_cartesian(xlim = c(min(plot_global_data$Date), global_plot_end_date)) +
  labs(title = "Global Master Chain Forecast (Market Trend)",
       subtitle = "Trend medio del mercato (Zoom a 2 Anni)", y = "Cost of sales per oz (aggregate, $/oz)", x = NULL) +
  theme_bw() + theme(legend.position = "top", plot.title = element_text(face = "bold", size = 14))

print(p_global)