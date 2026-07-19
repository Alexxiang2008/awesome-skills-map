const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json({ limit: '50mb' }));

// 数据存储目录
const DATA_DIR = path.join(__dirname, 'data');
if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR);
}

// 接收笔记数据
app.post('/api/sync/xiaohongshu/notes', (req, res) => {
    try {
        const { notes, total, timestamp } = req.body;

        // 保存为 JSON
        const filename = `xiaohongshu_notes_${timestamp}.json`;
        const filepath = path.join(DATA_DIR, filename);
        fs.writeFileSync(filepath, JSON.stringify(notes, null, 2));

        // 同时保存为 CSV
        const csvFilename = `xiaohongshu_notes_${timestamp}.csv`;
        const csvFilepath = path.join(DATA_DIR, csvFilename);
        const csvContent = generateCSV(notes);
        fs.writeFileSync(csvFilepath, csvContent);

        console.log(`✅ 已保存 ${total} 条笔记数据:`);
        console.log(`   📄 JSON: ${filename}`);
        console.log(`   📊 CSV: ${csvFilename}`);

        res.json({
            success: true,
            message: `成功保存 ${total} 条数据`,
            files: {
                json: filename,
                csv: csvFilename
            }
        });
    } catch (error) {
        console.error('❌ 保存失败:', error);
        res.status(500).json({
            success: false,
            message: error.message
        });
    }
});

// 生成 CSV
function generateCSV(notes) {
    const headers = ['笔记ID', '标题', '类型', '发布时间', '阅读量', '点赞数', '收藏数', '评论数', '分享数', '曝光量', '平均观看时长', '涨粉数', '封面点击率', '封面URL'];

    const rows = notes.map(note => [
        note.id || '',
        (note.title || '').replace(/"/g, '""'),
        note.type === 2 ? '视频' : '图文',
        note.post_time ? new Date(note.post_time).toLocaleString('zh-CN') : '',
        note.read_count || 0,
        note.like_count || 0,
        note.fav_count || 0,
        note.comment_count || 0,
        note.share_count || 0,
        note.imp_count || 0,
        note.view_time_avg || 0,
        note.increase_fans_count || 0,
        note.coverClickRate || 0,
        note.cover_url || '',
    ]);

    return '\ufeff' + [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');
}

// 查看已保存的文件列表
app.get('/api/files', (req, res) => {
    try {
        const files = fs.readdirSync(DATA_DIR);
        const fileList = files.map(filename => {
            const filepath = path.join(DATA_DIR, filename);
            const stats = fs.statSync(filepath);
            return {
                filename,
                size: stats.size,
                created: stats.birthtime,
                modified: stats.mtime
            };
        });

        res.json({
            success: true,
            files: fileList
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: error.message
        });
    }
});

// 健康检查
app.get('/health', (req, res) => {
    res.json({
        success: true,
        message: '服务运行正常',
        dataDir: DATA_DIR
    });
});

app.listen(PORT, () => {
    console.log('');
    console.log('🚀 小红书数据采集服务已启动');
    console.log('');
    console.log(`📡 服务地址: http://localhost:${PORT}`);
    console.log(`📁 数据目录: ${DATA_DIR}`);
    console.log('');
    console.log('💡 使用说明：');
    console.log('   1. 在浏览器中安装 Tampermonkey 脚本');
    console.log('   2. 访问小红书创作平台开始采集');
    console.log('   3. 点击"同步到本地服务"按钮');
    console.log('   4. 数据将自动保存到 data 目录');
    console.log('');
});
