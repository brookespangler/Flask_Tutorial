from flask import Flask, render_template, request
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text

app = Flask(__name__)
conn_str = "mysql://root:CSET115@localhost/boatdb"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()


# render a file
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


# get all boats
# this is done to handle requests for two routes -
@app.route('/boats/')
@app.route('/boats/<page>')
def get_boats(page=1):
    page = int(page)  # request params always come as strings. So type conversion is necessary.
    per_page = 10  # records to show per page
    boats = conn.execute(text(f"SELECT * FROM boats LIMIT {per_page} OFFSET {(page - 1) * per_page}")).all()
    print(boats)
    return render_template('boats.html', boats=boats, page=page, per_page=per_page)

@app.route('/create', methods=['GET'])
def create_get_request():
    return render_template('boats_create.html')


@app.route('/create', methods=['POST'])
def create_boat():
    # you can access the values with request.from.name
    # this name is the value of the name attribute in HTML form's input element
    # ex: print(request.form['id'])
    try:
        conn.execute(
            text("INSERT INTO boats values (:id, :name, :type, :owner_id, :rental_price)"),
            request.form
        )
        return render_template('boats_create.html', error=None, success="Data inserted successfully!")
    except Exception as e:
        error = e.orig.args[1]
        print(error)
        return render_template('boats_create.html', error=error, success=None)

#function for search 
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        keyword = request.form['query']
        result = conn.execute(
            text("SELECT * FROM boats WHERE name LIKE :q OR type LIKE :q"),
            {"q": f"%{keyword}%"}
        ).all()
        return render_template('boats_search.html', boats=result, query=keyword)
    return render_template('boats_search.html', boats=None)

#function for clickable boat page 
@app.route('/boats/<int:page>/<int:boat_id>')
def boat_detail(page, boat_id):
    boat = conn.execute(
        text("SELECT * FROM boats WHERE id = :id"),
        {"id": boat_id}
    ).fetchone()

    if boat:
        return render_template('boats_detail.html', boat=boat, page=page)
    else:
        return f"No boat found with ID {boat_id}", 404

#delete boat function
@app.route('/delete', methods=['GET', 'POST'])
def delete_boat():
    message = None
    if request.method == 'POST':
        boat_id = request.form['id']
        boat = conn.execute(text("SELECT * FROM boats WHERE id = :id"), {"id": boat_id}).fetchone()

        if boat:
            conn.execute(text("DELETE FROM boats WHERE id = :id"), {"id": boat_id})
            message = f"Boat with ID {boat_id} was deleted."
        else:
            message = f"No boat found with ID {boat_id}."

    return render_template('boats_delete.html', message=message)


@app.route('/update', methods=['GET', 'POST'])
def update_boat():
    boat = None
    message = None
    error = None

    if request.method == 'POST':
        form = request.form
        boat_id = form['id']

        boat = conn.execute(
            text("SELECT * FROM boats WHERE id = :id"),
            {"id": boat_id}
        ).fetchone()

        if boat:
            try:
                conn.execute(text("""
                    UPDATE boats
                    SET name = :name, type = :type, owner_id = :owner_id, rental_price = :rental_price
                    WHERE id = :id
                """), form)
                message = f"Boat with ID {boat_id} updated successfully."
            except Exception as e:
                error = str(e)
        else:
            error = f"No boat found with ID {boat_id}."

    return render_template('boats_update.html', boat=boat, message=message, error=error)

@app.route('/delete', methods=['GET'])
def delete_get_request():
    return render_template('boats_delete.html')


@app.route('/delete', methods=['POST'])
def delete_boat():
    try:
        conn.execute(
            text("DELETE FROM boats WHERE id = :id"),
            request.form
        )
        return render_template('boats_delete.html', error=None, success="Data deleted successfully!")
    except Exception as e:
        error = e.orig.args[1]
        print(error)
        return render_template('boats_delete.html', error=error, success=None)


if __name__ == '__main__':
    app.run(debug=True)
