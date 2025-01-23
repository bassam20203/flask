from flask import Flask, request, jsonify
import requests
import json
import base64

app = Flask(__name__)

# GitHub API details
GITHUB_TOKEN = "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"  # استبدل هذا بالـ GitHub Token الخاص بك
REPO_OWNER = "bassam20203"      # استبدل هذا باسم المستخدم الخاص بك
REPO_NAME = "flask"             # استبدل هذا باسم المستودع

# GitHub API base URL
GITHUB_API_BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents"

# CORS Headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response

# دالة لجلب محتوى الملف من GitHub
def get_file_content(stage):
    file_path = f"{stage}.json"  # اسم الملف بناءً على المرحلة
    url = f"{GITHUB_API_BASE_URL}/{file_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()["content"]
        return base64.b64decode(content).decode("utf-8")
    else:
        raise Exception(f"Failed to fetch file: {response.status_code} - {response.text}")

# دالة لحفظ التغييرات على الملف في GitHub
def save_file_content(stage, new_content, message="Updated file"):
    file_path = f"{stage}.json"  # اسم الملف بناءً على المرحلة
    url = f"{GITHUB_API_BASE_URL}/{file_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    # جلب SHA للملف الحالي
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch file SHA: {response.status_code} - {response.text}")
    sha = response.json()["sha"]

    # تحديث الملف
    data = {
        "message": message,
        "content": base64.b64encode(new_content.encode("utf-8")).decode("utf-8"),
        "sha": sha
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"Failed to update file: {response.status_code} - {response.text}")

# Get student result
@app.route('/get-result', methods=['GET'])
def get_result():
    stage = request.args.get('stage')
    rollNumber = request.args.get('rollNumber')

    if not stage or not rollNumber:
        return jsonify({"message": "البيانات غير مكتملة"}), 400

    try:
        content = get_file_content(stage)
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

# Update student data
@app.route('/update-student', methods=['POST'])
def update_student():
    data = request.get_json()
    stage = data.get('stage')
    rollNumber = data.get('rollNumber')
    updatedStudent = data.get('updatedStudent')

    if not stage or not rollNumber or not updatedStudent:
        return jsonify({"message": "البيانات غير مكتملة"}), 400

    try:
        content = get_file_content(stage)
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

        new_content = json.dumps(json_data, indent=2, ensure_ascii=False)
        save_file_content(stage, new_content, message=f"Updated student {rollNumber}")

        return jsonify({"message": "تم حفظ التعديلات بنجاح"}), 200
    except Exception as e:
        return jsonify({"message": "خطأ في قراءة أو حفظ الملف", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



