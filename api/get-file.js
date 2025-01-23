import fs from 'fs';
import path from 'path';

export default async function handler(req, res) {
    const { stage } = req.query;

    if (!stage) {
        return res.status(400).json({ message: "المرحلة غير محددة" });
    }

    const filePath = path.join(process.cwd(), 'JSON', `${stage}.json`);

    try {
        const content = fs.readFileSync(filePath, 'utf-8');
        return res.status(200).json({ content });
    } catch (error) {
        return res.status(500).json({ message: "خطأ في قراءة الملف", error: error.message });
    }
}