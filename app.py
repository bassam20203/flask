from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

# إعداد CORS يدويًا (يمكن استخدام flask-cors أيضًا)
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response

# رابط لتحديث بيانات الطالب
@app.route('/update-student', methods=['POST'])
def update_student():
    data = request.get_json()
    stage = data.get('stage')
    rollNumber = data.get('rollNumber')
    updatedStudent = data.get('updatedStudent')

    if not stage or not rollNumber or not updatedStudent:
        return jsonify({"message": "البيانات غير مكتملة"}), 400

    file_path = os.path.join('JSON', f'{stage}.json')

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)

        if not json_data.get('resalt') or not isinstance(json_data['resalt'], list):
            return jsonify({"message": "البيانات في الملف غير صالحة"}), 500

        student_index = next(
            (index for index, student in enumerate(json_data['resalt'])
             if student.get('rollNumber') and str(student['rollNumber']) == str(rollNumber)),
            -1
        )

        if student_index == -1:
            return jsonify({"message": "الطالب غير موجود"}), 404

        student = json_data['resalt'][student_index]
        for key, value in updatedStudent.items():
            if key in student:
                student[key] = value

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(json_data, file, indent=2)

        return jsonify({"message": "تم حفظ التعديلات بنجاح"}), 200

    except Exception as e:
        return jsonify({"message": "خطأ في قراءة أو حفظ الملف", "error": str(e)}), 500

# رابط للحصول على محتوى ملف
@app.route('/get-file', methods=['GET'])
def get_file():
    stage = request.args.get('stage')

    if not stage:
        return jsonify({"message": "المرحلة غير محددة"}), 400

    file_path = os.path.join('JSON', f'{stage}.json')

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return jsonify({"content": content}), 200
    except Exception as e:
        return jsonify({"message": "خطأ في قراءة الملف", "error": str(e)}), 500

# رابط لحفظ الملف
@app.route('/save-file', methods=['POST'])
def save_file():
    data = request.get_json()
    stage = data.get('stage')
    content = data.get('content')

    if not stage or not content:
        return jsonify({"message": "البيانات غير مكتملة"}), 400

    try:
        json.loads(content)  # تحقق من صحة JSON
    except ValueError as e:
        return jsonify({"message": "تنسيق JSON غير صحيح", "error": str(e)}), 400

    file_path = os.path.join('JSON', f'{stage}.json')

    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return jsonify({"message": "تم حفظ الملف بنجاح"}), 200
    except Exception as e:
        return jsonify({"message": "خطأ في حفظ الملف", "error": str(e)}), 500

# رابط للحصول على نتيجة الطالب
@app.route('/get-result', methods=['GET'])
def get_result():
    stage = request.args.get('stage')
    rollNumber = request.args.get('rollNumber')

    if not stage or not rollNumber:
        return jsonify({"message": "البيانات غير مكتملة"}), 400

    file_path = os.path.join('JSON', f'{stage}.json')

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)

        if not json_data.get('resalt') or not isinstance(json_data['resalt'], list):
            return jsonify({"message": "البيانات في الملف غير صالحة"}), 500

        student = next(
            (s for s in json_data['resalt']
             if s.get('rollNumber') and str(s['rollNumber']) == str(rollNumber)),
            None
        )

        if not student:
            return jsonify({"message": "الطالب غير موجود"}), 404

        return jsonify({"message": "تم العثور على الطالب", "student": student}), 200
    except Exception as e:
        return jsonify({"message": "خطأ في قراءة الملف", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)