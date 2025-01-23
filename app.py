from flask import Flask, request, jsonify
from flask_cors import CORS  # استيراد مكتبة CORS
import requests
import base64
import json

app = Flask(__name__)
CORS(app)  # تمكين CORS للتطبيق

# إعدادات GitHub
GITHUB_TOKEN = "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"  # استبدل بـ GitHub Token
REPO_OWNER = "bassam20203"  # اسم مالك المستودع
REPO_NAME = "flask"  # اسم المستودع
BRANCH = "main"  # اسم الفرع

# دالة لقراءة ملف من GitHub
def get_file_from_github(file_path):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}?ref={BRANCH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json().get("content", "")
        return base64.b64decode(content).decode("utf-8")
    else:
        raise Exception(f"خطأ في قراءة الملف: {response.status_code} - {response.text}")

# دالة لتحديث ملف في GitHub
def update_file_in_github(file_path, content, commit_message):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # الحصول على SHA الخاص بالملف
    response = requests.get(url, headers=headers, params={"ref": BRANCH})
    if response.status_code != 200:
        raise Exception(f"خطأ في جلب معلومات الملف: {response.status_code} - {response.text}")
    sha = response.json().get("sha", "")

    # تحديث الملف
    data = {
        "message": commit_message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "sha": sha,
        "branch": BRANCH
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        return True
    else:
        raise Exception(f"خطأ في تحديث الملف: {response.status_code} - {response.text}")

# تحديث بيانات طالب
@app.route('/update-student', methods=['POST'])
def update_student():
    data = request.get_json()
    stage = data.get('stage')
    rollNumber = data.get('rollNumber')
    updatedStudent = data.get('updatedStudent')

    if not stage or not rollNumber or not updatedStudent:
        return jsonify({"message": "البيانات غير مكتملة"}), 400

    file_path = f"JSON/{stage}.json"

    try:
        # قراءة الملف من GitHub
        content = get_file_from_github(file_path)
        json_data = json.loads(content)

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

        # تحديث الملف في GitHub
        update_file_in_github(file_path, json.dumps(json_data, indent=2, ensure_ascii=False), "Update student data")

        return jsonify({"message": "تم حفظ التعديلات بنجاح"}), 200
    except Exception as e:
        return jsonify({"message": "خطأ في قراءة أو حفظ الملف", "error": str(e)}), 500

# قراءة محتوى ملف
@app.route('/get-file', methods=['GET'])
def get_file():
    stage = request.args.get('stage')

    if not stage:
        return jsonify({"message": "المرحلة غير محددة"}), 400

    file_path = f"JSON/{stage}.json"

    try:
        content = get_file_from_github(file_path)
        return jsonify({"content": content}), 200
    except Exception as e:
        return jsonify({"message": "خطأ في قراءة الملف", "error": str(e)}), 500

# حفظ محتوى ملف
@app.route('/save-file', methods=['POST'])
def save_file():
    data = request.get_json()
    stage = data.get('stage')
    content = data.get('content')

    if not stage or not content:
        return jsonify({"message": "البيانات غير مكتملة"}), 400

    try:
        # التحقق من صحة JSON
        json.loads(content)
    except ValueError as e:
        return jsonify({"message": "تنسيق JSON غير صحيح", "error": str(e)}), 400

    file_path = f"JSON/{stage}.json"

    try:
        update_file_in_github(file_path, content, "Update file content")
        return jsonify({"message": "تم حفظ الملف بنجاح"}), 200
    except Exception as e:
        return jsonify({"message": "خطأ في حفظ الملف", "error": str(e)}), 500

# الحصول على نتيجة طالب
@app.route('/get-result', methods=['GET'])
def get_result():
    stage = request.args.get('stage')
    rollNumber = request.args.get('rollNumber')

    if not stage or not rollNumber:
        return jsonify({"message": "البيانات غير مكتملة"}), 400

    file_path = f"JSON/{stage}.json"

    try:
        content = get_file_from_github(file_path)
        json_data = json.loads(content)

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

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    