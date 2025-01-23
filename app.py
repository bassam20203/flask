# from flask import Flask, request, jsonify
# import os
# import json

# app = Flask(__name__)

# if not os.path.exists('JSON'):
#     os.makedirs('JSON')

# # CORS Headers
# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Headers', '*')
#     response.headers.add('Access-Control-Allow-Methods', '*')
#     return response

# # Update student data
# @app.route('/update-student', methods=['POST'])
# def update_student():
#     data = request.get_json()
#     stage = data.get('stage')
#     rollNumber = data.get('rollNumber')
#     updatedStudent = data.get('updatedStudent')

#     if not stage or not rollNumber or not updatedStudent:
#         return jsonify({"message": "البيانات غير مكتملة"}), 400

#     file_path = os.path.join('JSON', f'{stage}.json')

#     try:
#         with open(file_path, 'r', encoding='utf-8') as file:
#             json_data = json.load(file)

#         if not json_data.get('resalt') or not isinstance(json_data['resalt'], list):
#             return jsonify({"message": "البيانات في الملف غير صالحة"}), 500

#         student_index = next(
#             (index for index, student in enumerate(json_data['resalt'])
#              if student.get('rollNumber') and str(student['rollNumber']) == str(rollNumber)),
#             -1
#         )

#         if student_index == -1:
#             return jsonify({"message": "الطالب غير موجود"}), 404

#         student = json_data['resalt'][student_index]
#         for key, value in updatedStudent.items():
#             if key in student:
#                 student[key] = value

#         with open(file_path, 'w', encoding='utf-8') as file:
#             json.dump(json_data, file, indent=2, ensure_ascii=False)

#         return jsonify({"message": "تم حفظ التعديلات بنجاح"}), 200
#     except Exception as e:
#         return jsonify({"message": "خطأ في قراءة أو حفظ الملف", "error": str(e)}), 500

# # Get file content
# @app.route('/get-file', methods=['GET'])
# def get_file():
#     stage = request.args.get('stage')

#     if not stage:
#         return jsonify({"message": "المرحلة غير محددة"}), 400

#     file_path = os.path.join('JSON', f'{stage}.json')

#     try:
#         with open(file_path, 'r', encoding='utf-8') as file:
#             content = file.read()
#         return jsonify({"content": content}), 200
#     except Exception as e:
#         return jsonify({"message": "خطأ في قراءة الملف", "error": str(e)}), 500

# # Save file content
# @app.route('/save-file', methods=['POST'])
# def save_file():
#     data = request.get_json()  # Parse JSON body
#     stage = data.get('stage')
#     content = data.get('content')

#     if not stage or not content:
#         return jsonify({"message": "البيانات غير مكتملة"}), 400

#     try:
#         # Validate JSON content
#         json.loads(content)
#     except ValueError as e:
#         print(f"Invalid JSON content: {e}")  # Log the error
#         return jsonify({"message": "تنسيق JSON غير صحيح", "error": str(e)}), 400

#     file_path = os.path.join('JSON', f'{stage}.json')
#     print(f"Saving file to: {file_path}")  # Debugging line

#     try:
#         with open(file_path, 'w', encoding='utf-8') as file:
#             file.write(content)
#         return jsonify({"message": "تم حفظ الملف بنجاح"}), 200
#     except Exception as e:
#         print(f"Error saving file: {e}")  # Log the error
#         return jsonify({"message": "خطأ في حفظ الملف", "error": str(e)}), 500

# # Get student result
# @app.route('/get-result', methods=['GET'])
# def get_result():
#     stage = request.args.get('stage')
#     rollNumber = request.args.get('rollNumber')

#     if not stage or not rollNumber:
#         return jsonify({"message": "البيانات غير مكتملة"}), 400

#     file_path = os.path.join('JSON', f'{stage}.json')

#     try:
#         with open(file_path, 'r', encoding='utf-8') as file:
#             json_data = json.load(file)

#         if not json_data.get('resalt') or not isinstance(json_data['resalt'], list):
#             return jsonify({"message": "البيانات في الملف غير صالحة"}), 500

#         student = next(
#             (s for s in json_data['resalt']
#              if s.get('rollNumber') and str(s['rollNumber']) == str(rollNumber)),
#             None
#         )

#         if not student:
#             return jsonify({"message": "الطالب غير موجود"}), 404

#         return jsonify({"message": "تم العثور على الطالب", "student": student}), 200
#     except Exception as e:
#         return jsonify({"message": "خطأ في قراءة الملف", "error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

# مسار لجلب محتوى الملف
@app.route('/get-file', methods=['GET'])
def get_file():
    stage = request.args.get('stage')  # الحصول على المرحلة من الطلب
    if not stage:
        return jsonify({"error": "المرحلة غير محددة"}), 400

    # مسار ملف JSON بناءً على المرحلة
    file_path = os.path.join("JSON", f"{stage}.json")

    # التحقق من وجود الملف
    if not os.path.exists(file_path):
        return jsonify({"error": "الملف غير موجود"}), 404

    # قراءة الملف وإرجاع محتواه
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = json.load(file)

    return jsonify({"content": file_content}), 200

# مسار لحفظ الملف
@app.route('/save-file', methods=['POST'])
def save_file():
    data = request.json  # الحصول على البيانات المرسلة
    if not data or 'stage' not in data or 'content' not in data:
        return jsonify({"message": "المرحلة أو المحتوى غير محدد"}), 400

    stage = data['stage']
    content = data['content']

    # مسار ملف JSON بناءً على المرحلة
    file_path = os.path.join("JSON", f"{stage}.json")

    # حفظ المحتوى في الملف
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(content, file, ensure_ascii=False, indent=4)
        return jsonify({"message": "تم حفظ الملف بنجاح"}), 200
    except Exception as e:
        return jsonify({"message": f"حدث خطأ أثناء حفظ الملف: {str(e)}"}), 500

# مسار لتحديث بيانات الطالب
@app.route('/update-student', methods=['POST'])
def update_student():
    data = request.json  # الحصول على البيانات المرسلة
    if not data or 'student_id' not in data or 'new_data' not in data:
        return jsonify({"message": "بيانات الطالب غير مكتملة"}), 400

    student_id = data['student_id']
    new_data = data['new_data']

    # هنا يمكنك تحديث بيانات الطالب في قاعدة البيانات أو ملف JSON
    # هذا مثال بسيط:
    print(f"تم تحديث بيانات الطالب {student_id}: {new_data}")

    return jsonify({"message": "تم تحديث بيانات الطالب بنجاح"}), 200

# مسار لجلب نتيجة الطالب
@app.route('/get-result', methods=['GET'])
def get_result():
    student_id = request.args.get('student_id')  # الحصول على معرف الطالب من الطلب
    if not student_id:
        return jsonify({"error": "معرف الطالب غير محدد"}), 400

    # هنا يمكنك جلب نتيجة الطالب من قاعدة البيانات أو ملف JSON
    # هذا مثال بسيط:
    result = {
        "student_id": student_id,
        "grades": {"math": 90, "science": 85, "history": 78}
    }

    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)