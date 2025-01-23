import fetch from 'node-fetch';

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ message: "الطريقة غير مسموح بها" });
    }

    const { stage, content, githubToken } = req.body;

    if (!stage || !content || !githubToken) {
        return res.status(400).json({ message: "البيانات غير مكتملة" });
    }

    const repoUrl = `https://api.github.com/repos/bassam20203/flask/contents/JSON/${stage}.json`;
    const headers = {
        Authorization: `token ${githubToken}`,
        'Content-Type': 'application/json',
    };

    try {
        // جلب الملف الحالي من GitHub (إذا كان موجودًا)
        const fileResponse = await fetch(repoUrl, { headers });
        const fileData = await fileResponse.json();

        const updatedContent = Buffer.from(JSON.stringify(content, null, 2)).toString('base64');

        // حفظ الملف على GitHub
        const saveResponse = await fetch(repoUrl, {
            method: 'PUT',
            headers,
            body: JSON.stringify({
                message: 'Save file content',
                content: updatedContent,
                sha: fileData.sha || null,  // إذا كان الملف موجودًا، استخدم sha لتحديثه
            }),
        });

        if (!saveResponse.ok) {
            return res.status(500).json({ message: "خطأ في حفظ الملف على GitHub" });
        }

        return res.status(200).json({ message: "تم حفظ الملف بنجاح" });
    } catch (error) {
        return res.status(500).json({ message: "خطأ في حفظ الملف", error: error.message });
    }
}