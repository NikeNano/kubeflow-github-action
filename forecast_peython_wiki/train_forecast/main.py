import pandas as pd
from fbprophet import Prophet


@click.command()
def main():
     df = pd.read_csv('../examples/example_wp_log_peyton_manning.csv')
    m = Prophet()
    m.fit(df)
    future = m.make_future_dataframe(periods=365)
    forecast = m.predict(future)
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

 
if __name__ == "__main__":
    main()
