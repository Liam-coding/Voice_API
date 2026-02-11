// 🎤 实时音频质量监测工具
// 帮助诊断为什么翻译结果为空

console.log('🎤 音频质量实时监测工具已加载');

class AudioQualityMonitor {
    constructor() {
        this.audioContext = null;
        this.analyser = null;
        this.microphone = null;
        this.isMonitoring = false;
        this.qualityData = {
            volume: 0,
            clarity: 0,
            activity: 0
        };
    }
    
    async startMonitoring() {
        if (this.isMonitoring) return;
        
        try {
            console.log('🔍 开始音频质量监测...');
            
            // 获取音频上下文
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // 创建分析节点
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            
            // 连接麦克风到分析器
            this.microphone = this.audioContext.createMediaStreamSource(stream);
            this.microphone.connect(this.analyser);
            
            this.isMonitoring = true;
            console.log('✅ 音频监测已启动');
            
            // 开始实时分析
            this.analyzeAudio();
            
        } catch (error) {
            console.error('❌ 音频监测启动失败:', error);
        }
    }
    
    stopMonitoring() {
        if (!this.isMonitoring) return;
        
        this.isMonitoring = false;
        if (this.microphone) {
            this.microphone.disconnect();
        }
        if (this.audioContext) {
            this.audioContext.close();
        }
        console.log('⏹️ 音频监测已停止');
    }
    
    analyzeAudio() {
        if (!this.isMonitoring) return;
        
        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        const analyze = () => {
            if (!this.isMonitoring) return;
            
            this.analyser.getByteFrequencyData(dataArray);
            
            // 计算音量（平均振幅）
            let sum = 0;
            for (let i = 0; i < bufferLength; i++) {
                sum += dataArray[i];
            }
            const average = sum / bufferLength;
            const volume = Math.round((average / 255) * 100);
            
            // 计算清晰度（高频成分比例）
            let highFreqSum = 0;
            let lowFreqSum = 0;
            for (let i = 0; i < bufferLength; i++) {
                if (i > bufferLength * 0.7) {
                    highFreqSum += dataArray[i];
                } else {
                    lowFreqSum += dataArray[i];
                }
            }
            const clarity = lowFreqSum > 0 ? Math.round((highFreqSum / lowFreqSum) * 100) : 0;
            
            // 计算活跃度（超过阈值的频率数量）
            let activeBins = 0;
            for (let i = 0; i < bufferLength; i++) {
                if (dataArray[i] > 30) {
                    activeBins++;
                }
            }
            const activity = Math.round((activeBins / bufferLength) * 100);
            
            // 更新质量数据
            this.qualityData = { volume, clarity, activity };
            
            // 显示质量评估
            this.displayQualityAssessment();
            
            // 继续分析
            requestAnimationFrame(analyze);
        };
        
        analyze();
    }
    
    displayQualityAssessment() {
        const { volume, clarity, activity } = this.qualityData;
        
        // 音量评估
        const volumeLevel = volume > 60 ? '🔊 音量充足' : 
                           volume > 30 ? '🔉 音量适中' : 
                           volume > 10 ? '🔈 音量偏低' : '🔇 音量过低';
        
        // 清晰度评估
        const clarityLevel = clarity > 80 ? '🎯 清晰度高' :
                            clarity > 50 ? '✅ 清晰度良好' :
                            clarity > 20 ? '⚠️ 清晰度一般' : '❌ 清晰度低';
        
        // 活跃度评估
        const activityLevel = activity > 40 ? '🟢 活跃度高' :
                             activity > 20 ? '🟡 活跃度中等' :
                             activity > 5 ? '🟠 活跃度低' : '🔴 几乎无声';
        
        console.log(`📊 音频质量实时监测:`);
        console.log(`   ${volumeLevel} (${volume}%)`);
        console.log(`   ${clarityLevel} (${clarity}%)`);
        console.log(`   ${activityLevel} (${activity}%)`);
        
        // 综合评估
        const overallScore = (volume * 0.4 + clarity * 0.3 + activity * 0.3) / 100;
        const recommendation = overallScore > 0.7 ? '✅ 音频质量良好，适合语音识别' :
                              overallScore > 0.4 ? '⚠️ 音频质量一般，可能影响识别效果' :
                              '❌ 音频质量较差，建议改善录音条件';
        
        console.log(`   📈 综合评分: ${Math.round(overallScore * 100)}%`);
        console.log(`   💡 建议: ${recommendation}`);
        
        // 如果质量很差，给出具体建议
        if (overallScore < 0.4) {
            this.provideSpecificAdvice(volume, clarity, activity);
        }
    }
    
    provideSpecificAdvice(volume, clarity, activity) {
        console.log('\n🔧 具体改善建议:');
        
        if (volume < 30) {
            console.log('   🗣️ 请说话更大声一些');
        }
        if (volume > 80) {
            console.log('   🗣️ 请降低音量，避免失真');
        }
        if (clarity < 50) {
            console.log('   🎤 请靠近麦克风，减少环境噪音');
        }
        if (activity < 20) {
            console.log('   🎤 检查麦克风是否正常工作');
        }
        if (activity > 80) {
            console.log('   🌍 环境噪音可能过大，请选择更安静的地方');
        }
    }
}

// 创建全局监测实例
const audioMonitor = new AudioQualityMonitor();

// 添加到全局作用域
window.audioQualityMonitor = audioMonitor;

console.log('💡 使用方法:');
console.log('1. 运行 audioMonitor.startMonitoring() 开始监测');
console.log('2. 运行 audioMonitor.stopMonitoring() 停止监测');
console.log('3. 在录音时开启监测，实时查看音频质量');

// 简单的测试函数
window.testAudioQuality = async function() {
    console.log('🧪 开始音频质量测试...');
    await audioMonitor.startMonitoring();
    
    console.log('🎙️ 请对着麦克风说话3秒钟...');
    
    setTimeout(() => {
        audioMonitor.stopMonitoring();
        console.log('🏁 音频质量测试完成');
    }, 3000);
};

console.log('🎯 快速测试: 运行 testAudioQuality()');