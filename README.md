# OTOP Revenue Forecast Dashboard

## Project Overview

โปรเจคนี้เป็นระบบ Dashboard สำหรับวิเคราะห์และพยากรณ์รายได้ของสินค้า OTOP โดยใช้เทคนิค Machine Learning เพื่อช่วยแสดงแนวโน้มของรายได้ในอนาคต พร้อมทั้งมีการแสดงผลข้อมูลในรูปแบบกราฟเพื่อช่วยให้ผู้ใช้งานเข้าใจข้อมูลได้ง่ายขึ้น

ระบบถูกพัฒนาด้วย Python และใช้ Dash ในการสร้าง Web Dashboard สำหรับแสดงผลข้อมูลแบบ Interactive

## How to Run
1.python -m venv venv  

2.เปิดใช้งาน 
Windows : venv\Scripts\activate 
Mac/Linux : source venv/bin/activate

3.pip install -r requirements.txt 

4.python app.py

## Main Features

* แสดงผลข้อมูลรายได้ OTOP ในรูปแบบกราฟ
* การพยากรณ์รายได้ในอนาคตโดยใช้ Machine Learning ผ่าน PyCaret
* วิเคราะห์อัตราการเติบโตของรายได้ในแต่ละอำเภอ
* แสดง Top พื้นที่ที่มีการเติบโตสูงสุด
* สรุป Insight จากข้อมูลเพื่อช่วยในการวิเคราะห์แนวโน้ม

## Technologies Used

* Python
* Dash
* Plotly
* Pandas
* PyCaret

## Data Processing

ข้อมูลมีการทำความสะอาดก่อนนำมาใช้งาน เช่น

* การจัดรูปแบบประเภทข้อมูล
* การตรวจสอบค่าที่ผิดปกติ
* การเตรียมข้อมูลสำหรับการวิเคราะห์และการพยากรณ์

## Project Structure (Overview)

* `data/` : เก็บชุดข้อมูลที่ใช้ในโปรเจค
* `modules/` : โมดูลสำหรับการวิเคราะห์ข้อมูล
* `pages/` : หน้า Dashboard แต่ละส่วน
* `app.py` : ไฟล์หลักสำหรับรันระบบ Dash


## Purpose

โปรเจคนี้จัดทำขึ้นเพื่อใช้ในการศึกษาการวิเคราะห์ข้อมูลและการพยากรณ์แนวโน้มรายได้ OTOP โดยใช้ Machine Learning และการแสดงผลข้อมูลผ่าน Dashboard

## Web page
* Overview 
![alt text](image.png)
![alt text](image-1.png)

* Analysis 
![alt text](image-2.png)
![alt text](image-3.png)
![alt text](image-4.png)

* Forecast
![alt text](image-5.png)
![alt text](image-6.png)
![alt text](image-7.png)
