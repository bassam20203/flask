import fetch from 'node-fetch';

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ message: "الطريقة غير مسموح بها" });
    }

    const { stage, rollNumber, updatedStudent, githubToken } = req.body;

    if (!stage || !rollNumber || !updatedStudent || !githubToken) {
        return res.status(400).json({ message: "البيانات غير مكتملة" });
    }

    const repoUrl = `https://api.github.com/repos/bassam20203/flask/contents/JSON/${stage}.json`;
    const headers = {
        Authorization: `token ${githubToken}`,
        'Content-Type': 'application/json',
    };

    try {
        // جلب الملف الحالي من GitHub
        const fileResponse = await fetch(repoUrl, { headers });
        const fileData = await fileResponse.json();

        if (!fileData.content) {
            return res.status(500).json({ message: "الملف غير موجود أو غير قابل للقراءة" });
        }

        const content = Buffer.from(fileData.content, 'base64').toString('utf-8');
        const jsonData = JSON.parse(content);

        if (!jsonData.resalt || !Array.isArray(jsonData.resalt)) {
            return res.status(500).json({ message: "البيانات في الملف غير صالحة" });
        }

        const studentIndex = jsonData.resalt.findIndex(
            (student) => student.rollNumber && student.rollNumber.toString() === rollNumber.toString()
        );

        if (studentIndex === -1) {
            return res.status(404).json({ message: "الطالب غير موجود" });
        }

        const student = jsonData.resalt[studentIndex];
        for (const key in updatedStudent) {
            if (key in student) {
                student[key] = updatedStudent[key];
            }
        }

        const updatedContent = Buffer.from(JSON.stringify(jsonData, null, 2)).toString('base64');

        // تحديث الملف على GitHub
        const updateResponse = await fetch(repoUrl, {
            method: 'PUT',
            headers,
            body: JSON.stringify({
                message: 'Update student data',
                content: updatedContent,
                sha: fileData.sha,
            }),
        });

        if (!updateResponse.ok) {
            return res.status(500).json({ message: "خطأ في تحديث الملف على GitHub" });
        }

        return res.status(200).json({ message: "تم حفظ التعديلات بنجاح" });
    } catch (error) {
        return res.status(500).json({ message: "خطأ في قراءة أو حفظ الملف", error: error.message });
    }
}