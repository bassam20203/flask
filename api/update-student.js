import fs from 'fs';
import path from 'path';

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ message: "الطريقة غير مسموح بها" });
    }

    const { stage, rollNumber, updatedStudent } = req.body;

    if (!stage || !rollNumber || !updatedStudent) {
        return res.status(400).json({ message: "البيانات غير مكتملة" });
    }

    const filePath = path.join(process.cwd(), 'JSON', `${stage}.json`);

    try {
        const content = fs.readFileSync(filePath, 'utf-8');
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

        fs.writeFileSync(filePath, JSON.stringify(jsonData, null, 2), 'utf-8');
        return res.status(200).json({ message: "تم حفظ التعديلات بنجاح" });
    } catch (error) {
        return res.status(500).json({ message: "خطأ في قراءة أو حفظ الملف", error: error.message });
    }
}