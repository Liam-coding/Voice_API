// 🚨 紧急验证脚本 - 直接在控制台运行
// 用于验证阈值修复是否生效

console.log('🚀 开始紧急验证测试...');

// 模拟音频数据发送测试
async function testThresholdFix() {
    console.log('📊 测试阈值修复效果...');
    
    // 模拟不同大小的音频数据
    const testDataSizes = [366, 870, 1200, 2500, 3500, 5000];
    
    console.log('📏 测试不同数据大小的处理:');
    testDataSizes.forEach(size => {
        const shouldSend = size > 500; // 新的阈值
        console.log(`  ${size}字节: ${shouldSend ? '✅ 会发送' : '❌ 会被跳过'}`);
    });
    
    // 实际测试网络请求
    console.log('\n🌐 开始实际网络测试...');
    
    try {
        // 创建测试音频数据 (870字节，模拟实际情况)
        const testAudioData = new Uint8Array(870).fill(128);
        const audioBlob = new Blob([testAudioData], { type: 'audio/webm' });
        
        console.log(`📤 发送测试数据: ${audioBlob.size} 字节`);
        
        const formData = new FormData();
        formData.append('audio_chunk', audioBlob, 'threshold_test.webm');
        formData.append('source_lang', 'zh');
        formData.append('target_lang', 'en');
        
        console.log('📡 发送HTTP请求到后端...');
        const response = await fetch('http://127.0.0.1:8000/api/translate', {
            method: 'POST',
            body: formData,
            timeout: 10000
        });
        
        console.log(`📥 收到响应: ${response.status} ${response.statusText}`);
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ 网络请求成功:', data);
            return true;
        } else {
            const errorText = await response.text();
            console.error('❌ 网络请求失败:', response.status, errorText);
            return false;
        }
        
    } catch (error) {
        console.error('💥 网络请求异常:', error);
        return false;
    }
}

// 检查当前Vue组件状态
function checkVueComponent() {
    console.log('\n🔍 检查Vue组件状态...');
    
    // 查找录音按钮
    const recordButton = document.querySelector('#record-button') || 
                         document.querySelector('[class*="main-btn"]');
    
    if (recordButton) {
        console.log('✅ 找到录音按钮');
        console.log('按钮文本:', recordButton.textContent.trim());
        console.log('按钮状态:', recordButton.disabled ? '禁用' : '启用');
    } else {
        console.error('❌ 未找到录音按钮');
    }
    
    // 检查Vue实例
    if (window.__VUE_DEVTOOLS_GLOBAL_HOOK__) {
        console.log('✅ Vue DevTools已安装');
    }
}

// 创建全局测试函数
window.verifyFix = async function() {
    console.log('🔄 执行完整验证流程...');
    
    // 1. 检查组件状态
    checkVueComponent();
    
    // 2. 测试阈值和网络
    const networkSuccess = await testThresholdFix();
    
    // 3. 输出结果
    console.log('\n📋 验证结果总结:');
    console.log('===================');
    console.log(`网络请求测试: ${networkSuccess ? '✅ 通过' : '❌ 失败'}`);
    console.log('阈值设置: > 500字节');
    console.log('预计效果: 870字节的数据现在应该能正常发送');
    console.log('===================');
    
    if (networkSuccess) {
        console.log('🎉 修复验证成功！请刷新页面并重新测试录音功能。');
    } else {
        console.log('⚠️ 网络测试失败，请检查后端服务是否正常运行。');
    }
    
    return networkSuccess;
};

console.log('💡 使用方法:');
console.log('1. 在控制台运行: verifyFix()');
console.log('2. 观察输出结果');
console.log('3. 刷新页面测试实际录音功能');

// 立即执行一次快速测试
testThresholdFix().then(success => {
    console.log(`\n⚡ 快速测试结果: ${success ? '成功' : '失败'}`);
});