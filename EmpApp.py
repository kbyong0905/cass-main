from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')


@app.route("/aboutus", methods=['POST'])
def about():
    return render_template('About Us.html')

@app.route("/getemp", methods=['GET', 'POST'])
def getemp():
    resultdata= ""
    
    select_stmt = "SELECT * FROM employee"
    cursor = db_conn.cursor()
            
    try:
        cursor.execute(select_stmt)
        resultdata=cursor.fetchall()
        for resultEmp in cursor:
            print(resultEmp)

    except Exception as e:
        return str(e)
        
    finally:
        cursor.close()

    return render_template('GetEmp.html', result=resultdata)


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']

    emp_image_file = request.files['emp_image_file']

    if emp_image_file.filename == "":
        return "Please select a file"

    try:
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)
            
            insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, 'Active')"
            cursor = db_conn.cursor()
            cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
            db_conn.commit()

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)

# Get Employee Information
@app.route("/fetchdata",methods=['GET','POST'])
def getEmp():
     emp_id = request.form['emp_id']
    
     select_stmt = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"
     cursor = db_conn.cursor()
            
     try:
         cursor.execute(select_stmt, { 'emp_id': int(emp_id) })
         for result in cursor:
            print(result)

     except Exception as e:
        return str(e)
        
     finally:
        cursor.close()

        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)
        
     return render_template('GetEmpOutput.html', result=result, image_url=object_url)


@app.route("/update", methods=['POST'])
def EditStaff():
    emp_id= request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    status = request.form['status']
    edit_image = request.files['emp_image_file']

    #if no image uploaded
    if edit_image.filename == "":
        try:
            insert_sql = "UPDATE employee SET first_name= %s, last_name=%s, pri_skill=%s, location=%s, status=%s WHERE emp_id = %s"
            cursor = db_conn.cursor()
            cursor.execute(insert_sql, (first_name, last_name, pri_skill, location, status, emp_id))
            db_conn.commit()

        except Exception as e:
            return str(e)
            
        finally:
            cursor.close()

    #else got image upload, run image file query
    else:
        try:
            
            # Upload image file in S3 #
            image_file_name = "emp-id-" + str(emp_id) + "_image_file"
            s3 = boto3.resource('s3')

            insert_sql = "UPDATE employee SET first_name=%s, last_name=%s, pri_skill=%s, location=%s, status=%s WHERE emp_id = %s"
            cursor = db_conn.cursor()
            cursor.execute(insert_sql, (first_name, last_name, pri_skill, location, status, emp_id))
            db_conn.commit()
            
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=image_file_name, Body=edit_image)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])
            
            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location
        except Exception as e:
            return str(e)
        
        finally:
            cursor.close()


    select_stmt = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"
    cursor = db_conn.cursor()
            
    try:
        cursor.execute(select_stmt, { 'emp_id': int(emp_id) })
        for result in cursor:
            print(result)

    except Exception as e:
        return str(e)
            
    finally:
        cursor.close()

    emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
    s3 = boto3.resource('s3')

    try:
        print("Data inserted in MySQL RDS... uploading image to S3...")
        bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
        s3_location = (bucket_location['LocationConstraint'])
        if s3_location is None:
            s3_location = ''
        else:
            s3_location = '-' + s3_location

        object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
        s3_location,
        custombucket,
        emp_image_file_name_in_s3)

    except Exception as e:
        return str(e)

    print(object_url)
    print(emp_id)
    return render_template('GetEmpOutput.html', result=result, image_url=object_url)


# Edit Employee Done
@app.route("/update/",methods=['GET','POST'])
def editEmpDone():
    
    return render_template('EditEmp.html')
    
@app.route('/delete/<string:ID>',methods=['POST','GET'])
def delete(ID):
    s3_client = boto3.client("s3")
    image_file_name = "emp-id-" + str(ID) + "_image_file"
    response = s3_client.delete_object(Bucket=custombucket, Key=image_file_name)
    delete_sql = "DELETE FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()
    cursor.execute(delete_sql, (ID))
    db_conn.commit()
    return render_template('GetEmp.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
