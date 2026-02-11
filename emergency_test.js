// 🚨 紧急按钮测试脚本
// 在浏览器控制台直接运行这个脚本来测试按钮功能

console.log('🚀 开始紧急按钮功能测试...');

// 1. 检查按钮元素是否存在
const recordButton = document.querySelector('#record-button') || document.querySelector('[class*="main-btn"]');
if (recordButton) {
    console.log('✅ 找到录音按钮:', recordButton);
    
    // 2. 检查当前绑定的事件
    console.log('📋 当前按钮事件监听器:');
    if (getEventListeners) {
        console.log(getEventListeners(recordButton));
    }
    
    // 3. 添加测试事件监听器
    const testHandler = function(event) {
        console.log('🎯 测试事件处理器被触发!', {
            eventType: event.type,
            timeStamp: event.timeStamp,
            target: event.target
        });
        
        // 显示视觉反馈
        recordButton.style.transform = 'scale(0.95)';
        setTimeout(() => {
            recordButton.style.transform = 'scale(1)';
        }, 100);
        
        // 尝试触发实际的录音功能
        try {
            // 查找Vue组件实例
            const vueInstance = recordButton.__vueParentComponent;
            if (vueInstance) {
                console.log('🔍 找到Vue实例，尝试调用方法...');
                // 尝试调用组件方法
                if (vueInstance.ctx && vueInstance.ctx.start) {
                    vueInstance.ctx.start();
                }
            }
        } catch (error) {
            console.log('⚠️ Vue实例调用失败:', error);
        }
    };
    
    // 移除旧的监听器（如果有的话）
    recordButton.removeEventListener('click', testHandler);
    // 添加新的测试监听器
    recordButton.addEventListener('click', testHandler);
    
    console.log('✅ 测试监听器已添加');
    
    // 4. 手动触发一次点击测试
    console.log('🖱️ 手动触发点击测试...');
    recordButton.click();
    
} else {
    console.error('❌ 未找到录音按钮!');
    console.log('🔍 页面上所有按钮元素:');
    document.querySelectorAll('button').forEach((btn, index) => {
        console.log(`${index + 1}.`, btn.textContent.trim(), btn);
    });
}

// 5. 测试直接录音功能
async function testDirectRecording() {
    console.log('🎙️ 开始直接录音测试...');
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        console.log('✅ 麦克风权限获取成功');
        
        const mediaRecorder = new MediaRecorder(stream);
        console.log('✅ MediaRecorder创建成功');
        
        mediaRecorder.ondataavailable = async (event) => {
            if (event.data.size > 0) {
                console.log('🔊 收到录音数据:', event.data.size, '字节');
                
                // 直接发送到后端测试
                const formData = new FormData();
                formData.append('audio_chunk', event.data, 'direct_test.webm');
                formData.append('source_lang', 'zh');
                formData.append('target_lang', 'en');
                
                try {
                    console.log('📤 发送测试请求到后端...');
                    const response = await fetch('http://127.0.0.1:8000/api/translate', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        console.log('✅ 后端响应:', result);
                    } else {
                        console.error('❌ 后端返回错误:', response.status);
                    }
                } catch (error) {
                    console.error('💥 网络请求失败:', error);
                }
            }
        };
        
        mediaRecorder.start(1000); // 每秒获取一次数据
        console.log('✅ 录音已开始');
        
        // 5秒后停止
        setTimeout(() => {
            mediaRecorder.stop();
            stream.getTracks().forEach(track => track.stop());
            console.log('⏹️ 录音已停止');
        }, 5000);
        
    } catch (error) {
        console.error('❌ 录音测试失败:', error);
    }
}

// 6. 创建全局测试函数
window.testButtonFunction = function() {
    console.log('🔄 全局测试函数被调用');
    testDirectRecording();
};

console.log('💡 可以在控制台运行: testButtonFunction() 来测试录音功能');
console.log('💡 或者直接点击页面上的录音按钮测试');

// 7. 检查页面其他相关信息
console.log('📊 页面状态检查:');
console.log('- 当前URL:', window.location.href);
console.log('- 页面标题:', document.title);
console.log('- Vue DevTools:', window.__VUE_DEVTOOLS_GLOBAL_HOOK__ ? '已安装' : '未安装');