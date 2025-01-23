import fs from 'fs';
import path from 'path';

export default async function handler(req, res) {
    const { stage, rollNumber } = req.query;

    if (!stage || !rollNumber) {
        return res.status(400).json({ message: "البيانات غير مكتملة" });
    }

    const filePath = path.join(process.cwd(), 'JSON', `${stage}.json`);

    try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const jsonData = JSON.parse(content);

        if (!jsonData.resalt || !Array.isArray(jsonData.resalt)) {
            return res.status(500).json({ message: "البيانات في الملف غير صالحة" });
        }

        const student = jsonData.resalt.find(
            (s) => s.rollNumber && s.rollNumber.toString() === rollNumber.toString()
        );

        if (!student) {
            return res.status(404).json({ message: "الطالب غير موجود" });
        }

        return res.status(200).json({ message: "تم العثور على الطالب", student });
    } catch (error) {
        return res.status(500).json({ message: "خطأ في قراءة الملف", error: error.message });
    }
}