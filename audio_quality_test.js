// 🎤 音频质量测试脚本
// 在浏览器控制台运行，用于测试不同音频内容的识别效果

console.log('🎙️ 开始音频质量测试...');

async function testAudioQuality() {
    console.log('📊 测试不同音频内容的识别效果');
    
    // 测试不同类型的数据
    const testCases = [
        {
            name: '静音数据',
            data: new Uint8Array(4000).fill(0),
            description: '全零数据，模拟静音'
        },
        {
            name: '随机噪音',
            data: new Uint8Array(4000).map(() => Math.floor(Math.random() * 256)),
            description: '随机数据，模拟噪音'
        },
        {
            name: '简单音频模式',
            data: new Uint8Array(4000).map((_, i) => Math.sin(i * 0.1) * 127 + 128),
            description: '正弦波模式，模拟简单音频'
        }
    ];
    
    for (const testCase of testCases) {
        console.log(`\n🧪 测试: ${testCase.name}`);
        console.log(`📄 描述: ${testCase.description}`);
        
        try {
            const blob = new Blob([testCase.data], { type: 'audio/webm' });
            console.log(`💾 数据大小: ${blob.size} 字节`);
            
            const formData = new FormData();
            formData.append('audio_chunk', blob, `${testCase.name}.webm`);
            formData.append('source_lang', 'zh');
            formData.append('target_lang', 'en');
            
            console.log('📤 发送测试数据...');
            const response = await fetch('http://127.0.0.1:8000/api/translate', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            console.log(`📥 响应状态: ${response.status}`);
            console.log(`💬 翻译结果: "${result.translation}"`);
            console.log(`📄 原文: "${result.original}"`);
            console.log(`📊 状态: ${result.status}`);
            
            if (result.translation) {
                console.log('✅ 识别成功！');
            } else {
                console.log('❌ 未识别到有效内容');
            }
            
        } catch (error) {
            console.error(`💥 测试失败: ${error.message}`);
        }
        
        // 等待一点时间再进行下一个测试
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
}

// 测试真实录音数据
async function testRealRecording() {
    console.log('\n🎙️ 测试真实录音数据...');
    
    try {
        console.log('🔍 请求麦克风权限...');
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                sampleRate: 16000
            } 
        });
        
        console.log('✅ 麦克风权限获取成功');
        
        // 检查支持的MIME类型
        const mimeTypes = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg'];
        let selectedMimeType = '';
        for (let mimeType of mimeTypes) {
            if (MediaRecorder.isTypeSupported(mimeType)) {
                selectedMimeType = mimeType;
                break;
            }
        }
        
        const mediaRecorder = new MediaRecorder(stream, { mimeType: selectedMimeType });
        console.log(`🔧 使用音频格式: ${selectedMimeType}`);
        
        // 收集录音数据
        const audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
                console.log(`🔊 收到录音数据: ${event.data.size} 字节`);
            }
        };
        
        // 开始录音
        mediaRecorder.start(1000);
        console.log('✅ 录音已开始，请说话5秒钟...');
        
        // 5秒后停止
        await new Promise(resolve => {
            setTimeout(() => {
                mediaRecorder.stop();
                stream.getTracks().forEach(track => track.stop());
                resolve();
            }, 5000);
        });
        
        console.log('⏹️ 录音结束');
        
        // 合并所有录音数据
        if (audioChunks.length > 0) {
            const fullAudioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            console.log(`📦 总录音大小: ${fullAudioBlob.size} 字节`);
            
            // 发送到后端测试
            const formData = new FormData();
            formData.append('audio_chunk', fullAudioBlob, 'real_recording.webm');
            formData.append('source_lang', 'zh');
            formData.append('target_lang', 'en');
            
            console.log('📤 发送真实录音数据...');
            const response = await fetch('http://127.0.0.1:8000/api/translate', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            console.log(`📥 后端响应:`, result);
            
            if (result.translation) {
                console.log(`🎉 成功识别: "${result.translation}"`);
            } else {
                console.log('❌ 未能识别有效内容');
                console.log('💡 建议: 请说得更清楚、更大声一些');
            }
        } else {
            console.log('❌ 没有收集到录音数据');
        }
        
    } catch (error) {
        console.error('❌ 录音测试失败:', error);
    }
}

// 创建全局测试函数
window.testAudioRecognition = async function() {
    console.log('🚀 开始完整的音频识别测试...');
    
    // 先测试合成数据
    await testAudioQuality();
    
    // 再测试真实录音
    await testRealRecording();
    
    console.log('\n📋 测试完成总结:');
    console.log('====================');
    console.log('如果合成数据也无法识别，说明是后端配置问题');
    console.log('如果只有真实录音无法识别，说明是录音质量问题');
    console.log('====================');
};

console.log('💡 使用方法:');
console.log('在控制台运行: testAudioRecognition()');
console.log('或者单独运行: testAudioQuality() 或 testRealRecording()');

// 立即执行快速测试
testAudioQuality();