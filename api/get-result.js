import fetch from 'node-fetch';

export default async function handler(req, res) {
    const { stage, githubToken } = req.query;

    if (!stage || !githubToken) {
        return res.status(400).json({ message: "البيانات غير مكتملة" });
    }

    const repoUrl = `https://api.github.com/repos/bassam20203/flask/contents/JSON/${stage}.json`;
    const headers = {
        Authorization: `token ${githubToken}`,
    };

    try {
        const fileResponse = await fetch(repoUrl, { headers });
        const fileData = await fileResponse.json();

        if (!fileData.content) {
            return res.status(500).json({ message: "الملف غير موجود أو غير قابل للقراءة" });
        }

        const content = Buffer.from(fileData.content, 'base64').toString('utf-8');
        return res.status(200).json({ content });
    } catch (error) {
        return res.status(500).json({ message: "خطأ في قراءة الملف", error: error.message });
    }
}