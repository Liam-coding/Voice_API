// 🌐 CORS修复验证脚本
// 用于测试跨域请求是否正常工作

console.log('🌐 开始CORS配置测试...');

async function testCORS() {
    console.log('🧪 测试CORS配置...');
    
    try {
        // 测试OPTIONS预检请求
        console.log('1. 测试OPTIONS预检请求...');
        const optionsResponse = await fetch('http://127.0.0.1:8000/health', {
            method: 'OPTIONS'
        });
        console.log(`   OPTIONS响应状态: ${optionsResponse.status}`);
        
        // 测试GET请求
        console.log('2. 测试GET健康检查...');
        const getResponse = await fetch('http://127.0.0.1:8000/health');
        console.log(`   GET响应状态: ${getResponse.status}`);
        
        if (getResponse.ok) {
            const data = await getResponse.json();
            console.log(`   GET响应数据:`, data);
        }
        
        // 测试POST请求（使用简单数据）
        console.log('3. 测试POST请求...');
        const postData = new FormData();
        postData.append('source_lang', 'zh');
        postData.append('target_lang', 'en');
        
        // 创建最小的测试音频数据
        const testAudio = new Uint8Array(100).fill(0);
        const audioBlob = new Blob([testAudio], { type: 'audio/webm' });
        postData.append('audio_chunk', audioBlob, 'test.webm');
        
        const postResponse = await fetch('http://127.0.0.1:8000/api/translate', {
            method: 'POST',
            body: postData
        });
        
        console.log(`   POST响应状态: ${postResponse.status}`);
        
        if (postResponse.ok) {
            const result = await postResponse.json();
            console.log(`   POST响应数据:`, result);
            console.log('✅ CORS配置正常！');
        } else {
            const errorText = await postResponse.text();
            console.log(`   POST错误响应: ${postResponse.status} - ${errorText}`);
            console.log('❌ CORS可能仍有问题');
        }
        
    } catch (error) {
        console.error('💥 CORS测试失败:', error);
        console.log('可能的原因:');
        console.log('- 后端服务未运行');
        console.log('- CORS配置未生效（需要重启后端）');
        console.log('- 网络连接问题');
    }
}

// 测试前端到后端的完整流程
async function testFullFlow() {
    console.log('\n🔄 测试完整工作流程...');
    
    // 1. 先测试后端健康状态
    try {
        const healthResponse = await fetch('http://127.0.0.1:8000/health');
        if (!healthResponse.ok) {
            console.log('❌ 后端服务不可用，请先启动后端服务');
            return;
        }
        console.log('✅ 后端服务正常');
    } catch (error) {
        console.log('❌ 无法连接到后端服务');
        return;
    }
    
    // 2. 测试录音功能
    console.log('🎙️ 测试录音功能...');
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        console.log('✅ 麦克风权限获取成功');
        
        const mediaRecorder = new MediaRecorder(stream);
        const chunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                chunks.push(event.data);
                console.log(`🔊 收到音频数据: ${event.data.size} 字节`);
            }
        };
        
        mediaRecorder.start(1000);
        console.log('✅ 录音开始，请说话2秒...');
        
        setTimeout(() => {
            mediaRecorder.stop();
            stream.getTracks().forEach(track => track.stop());
            
            if (chunks.length > 0) {
                const fullBlob = new Blob(chunks, { type: 'audio/webm' });
                console.log(`📦 录音完成，总大小: ${fullBlob.size} 字节`);
                
                // 3. 测试发送到后端
                console.log('📤 测试发送到后端...');
                const formData = new FormData();
                formData.append('audio_chunk', fullBlob, 'test_recording.webm');
                formData.append('source_lang', 'zh');
                formData.append('target_lang', 'en');
                
                fetch('http://127.0.0.1:8000/api/translate', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    console.log(`📥 后端响应状态: ${response.status}`);
                    return response.json();
                })
                .then(data => {
                    console.log('📥 后端响应数据:', data);
                    if (data.translation) {
                        console.log(`🎉 翻译成功: "${data.translation}"`);
                    } else {
                        console.log('⚠️ 翻译结果为空，可能是音频质量问题');
                    }
                })
                .catch(error => {
                    console.error('❌ 发送到后端失败:', error);
                });
            }
        }, 2000);
        
    } catch (error) {
        console.error('❌ 录音测试失败:', error);
    }
}

// 创建全局测试函数
window.testCORSFix = async function() {
    console.log('🚀 开始CORS修复验证...');
    await testCORS();
    await testFullFlow();
};

console.log('💡 使用方法:');
console.log('1. 确保后端服务正在运行');
console.log('2. 在控制台运行: testCORSFix()');
console.log('3. 观察测试结果');

// 立即执行CORS测试
testCORS();