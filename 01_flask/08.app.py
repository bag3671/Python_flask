from flask import Flask, render_template
import os
app = Flask(__name__)

@app.route('/carousel')
def child1():
    img_file1 = 'img/ny.jpg'
    img_file2 = 'img/cica.jpg'
    img_file3 = 'img/la.jpg'
    return render_template(
        '08.carousel.html',img_file1=img_file1,img_file2=img_file2,img_file3=img_file3
    )
@app.route('/loginform')
def child2():
    return render_template(
        '08.loginform.html'
    )
@app.route('/filterable_table')
def child3():
    return render_template(
        '08.filterable_table.html'
    )
if __name__ == '__main__':
    app.run(debug=True)