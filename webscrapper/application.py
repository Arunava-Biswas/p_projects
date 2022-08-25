from flask import Flask, request, render_template
import pandas as pd
import webscraper

app = Flask(__name__)
# https://github.com/c17hawke/flask-based-wordcloud-generator (for html and css part)
# https://www.youtube.com/watch?v=ng2o98k983k (Corey Schaefer Beautifulsoup)
# https://www.youtube.com/watch?v=syTIzS4AIpM (Krish Naik Web Scraping1)
# https://www.youtube.com/watch?v=zHjnc2ZwbGA (Krish Naik Web Scraping2)

# Creating routes
@app.route('/', methods=['GET'])
@app.route('/index')
def home():
    return render_template('index.html')


@app.route('/results', methods=['POST', 'GET'])
def data_search():
    if request.method == 'POST':
        try:
            search_string = request.form['content']
            search_str = search_string.replace(" ", "+")

            # Creating connection and loading to the server
            data = webscraper.Data(search_str)
            links = data.creating_link()
            res = data.data_fetching(links)
            df = data.create_df(res)
            data.loading_server(df)

            # Pulling data from the server and display
            results = data.data_show()
            df1 = pd.DataFrame(results)
            # To remove the id and page_no as these are not meaningful
            df1.drop(['_id', 'Page_no'], axis=1, inplace=True)
            df1.reset_index(drop=True, inplace=True)
        except Exception as err:
            print(err)
            return render_template("404.html")
        else:
            return render_template('results.html', tables=[df1.to_html(classes='data')], titles=df1.columns.values)
        finally:
            # to clear the database at the end of the result shown
            data.data_del()


if __name__ == "__main__":
    app.run(debug=True)
