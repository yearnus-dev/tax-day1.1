import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, TrendingUp, Clock, Flame, MessageCircle, Send, Target } from 'lucide-react';

const WalkingDashboard = () => {
  const [messages, setMessages] = useState([
    { type: 'bot', text: '안녕하세요! 👋 걷기운동에 대해 궁금한 점을 물어보세요.' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentSteps, setCurrentSteps] = useState(6543);
  const [dailyGoal] = useState(10000);

  // 주간 걸음 수 데이터
  const weeklyData = [
    { day: '월', steps: 8234, goal: 10000 },
    { day: '화', steps: 9821, goal: 10000 },
    { day: '수', steps: 7453, goal: 10000 },
    { day: '목', steps: 10234, goal: 10000 },
    { day: '금', steps: 8976, goal: 10000 },
    { day: '토', steps: 11543, goal: 10000 },
    { day: '일', steps: 6543, goal: 10000 }
  ];

  // 시간대별 활동량
  const hourlyData = [
    { time: '06:00', steps: 1200 },
    { time: '09:00', steps: 800 },
    { time: '12:00', steps: 1500 },
    { time: '15:00', steps: 900 },
    { time: '18:00', steps: 1800 },
    { time: '21:00', steps: 343 }
  ];

  // 목표 달성률
  const achievementData = [
    { name: '달성', value: currentSteps },
    { name: '남은 목표', value: Math.max(0, dailyGoal - currentSteps) }
  ];

  const COLORS = ['#667eea', '#e0e7ff'];

  // 실시간 걸음 수 시뮬레이션
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSteps(prev => Math.min(dailyGoal, prev + Math.floor(Math.random() * 50)));
    }, 5000);
    return () => clearInterval(interval);
  }, [dailyGoal]);

  const generateResponse = (userMessage) => {
    const msg = userMessage.toLowerCase();
    
    if (msg.includes('걸음') || msg.includes('보수')) {
      return "20대~40대 남성의 당뇨병 예방을 위한 하루 권장 걸음 수는 약 7,000~10,000보입니다.\n\n• 최소 목표: 7,000보\n• 이상적 목표: 10,000보\n• 현재 대시보드에서 실시간으로 걸음 수를 확인하실 수 있습니다!";
    }
    if (msg.includes('시간') || msg.includes('30대') || msg.includes('20대') || msg.includes('40대')) {
      return "20대~40대 남성의 권장 걷기시간은 하루 30분 이상, 주 5일 이상입니다.\n\n한 번에 30분이 어렵다면 10분씩 3회로 나눠도 좋습니다. 위 차트에서 주간 운동 패턴을 확인해보세요!";
    }
    if (msg.includes('식후') || msg.includes('밥') || msg.includes('식사')) {
      return "식후 걷기는 혈당 급상승을 막고 인슐린 감수성을 높이는 데 도움됩니다.\n\n• 식사 후 10~15분 걷기\n• 저녁 식사 후 걷기가 특히 효과적입니다.\n• 시간대별 차트에서 12시, 18시 이후 활동량을 늘려보세요!";
    }
    if (msg.includes('방법') || msg.includes('어떻게') || msg.includes('효과적')) {
      return "효과적인 걷기 운동 방법:\n\n1. 가슴을 펴고 시선은 전방 15m\n2. 팔은 자연스럽게 흔들기\n3. 발뒤꿈치부터 착지 후 발가락으로 밀기\n4. 분당 100~120보 속도 유지";
    }
    if (msg.includes('당뇨') || msg.includes('예방') || msg.includes('효과')) {
      return "걷기운동은 당뇨병 예방에 매우 효과적입니다!\n\n• 혈당 조절 개선\n• 체중 관리\n• 심혈관 건강 향상\n• 인슐린 감수성 증가";
    }
    
    return "안녕하세요! 걷기운동에 대해 더 궁금한 점을 물어보세요.\n\n추천 질문: '하루 권장 걸음 수', '식후 걷기 효과', '효과적인 걷기 방법'";
  };

  const handleSend = () => {
    if (!inputValue.trim()) return;

    setMessages(prev => [...prev, { type: 'user', text: inputValue }]);
    setInputValue('');
    setIsTyping(true);

    setTimeout(() => {
      const response = generateResponse(inputValue);
      setMessages(prev => [...prev, { type: 'bot', text: response }]);
      setIsTyping(false);
    }, 1000);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  const progressPercentage = Math.min(100, (currentSteps / dailyGoal) * 100);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl shadow-lg p-8 mb-6 text-white">
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
            <Activity className="w-8 h-8" />
            당뇨병 예방 걷기운동 대시보드
          </h1>
          <p className="opacity-90">실시간 통계 + AI 챗봇 가이드</p>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm font-medium">오늘 걸음 수</p>
                <p className="text-3xl font-bold text-gray-800 mt-1">{currentSteps.toLocaleString()}</p>
                <p className="text-xs text-gray-400 mt-1">목표: {dailyGoal.toLocaleString()}보</p>
              </div>
              <Activity className="w-12 h-12 text-purple-500 opacity-20" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm font-medium">달성률</p>
                <p className="text-3xl font-bold text-gray-800 mt-1">{progressPercentage.toFixed(0)}%</p>
                <p className="text-xs text-gray-400 mt-1">일일 목표 기준</p>
              </div>
              <Target className="w-12 h-12 text-blue-500 opacity-20" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm font-medium">운동 시간</p>
                <p className="text-3xl font-bold text-gray-800 mt-1">42분</p>
                <p className="text-xs text-gray-400 mt-1">권장: 30분 이상</p>
              </div>
              <Clock className="w-12 h-12 text-green-500 opacity-20" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-orange-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm font-medium">소모 칼로리</p>
                <p className="text-3xl font-bold text-gray-800 mt-1">287</p>
                <p className="text-xs text-gray-400 mt-1">kcal</p>
              </div>
              <Flame className="w-12 h-12 text-orange-500 opacity-20" />
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-gray-700">일일 목표 진행률</h3>
            <span className="text-sm font-medium text-purple-600">{currentSteps.toLocaleString()} / {dailyGoal.toLocaleString()}보</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-purple-500 to-blue-500 h-4 rounded-full transition-all duration-500 flex items-center justify-end pr-2"
              style={{ width: `${progressPercentage}%` }}
            >
              {progressPercentage > 10 && <span className="text-xs text-white font-bold">{progressPercentage.toFixed(0)}%</span>}
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Weekly Steps Chart */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-purple-600" />
              주간 걸음 수 추이
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="day" stroke="#888" />
                <YAxis stroke="#888" />
                <Tooltip />
                <Bar dataKey="steps" fill="#667eea" radius={[8, 8, 0, 0]} />
                <Bar dataKey="goal" fill="#e0e7ff" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Hourly Activity Chart */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <Clock className="w-5 h-5 text-blue-600" />
              시간대별 활동량
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={hourlyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="time" stroke="#888" />
                <YAxis stroke="#888" />
                <Tooltip />
                <Line type="monotone" dataKey="steps" stroke="#3b82f6" strokeWidth={3} dot={{ fill: '#3b82f6', r: 5 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chatbot + Achievement Chart */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Achievement Pie Chart */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <Target className="w-5 h-5 text-green-600" />
              목표 달성률
            </h3>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={achievementData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {achievementData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="text-center mt-2">
              <p className="text-2xl font-bold text-purple-600">{progressPercentage.toFixed(0)}%</p>
              <p className="text-sm text-gray-500">오늘 달성률</p>
            </div>
          </div>

          {/* Chatbot */}
          <div className="lg:col-span-2 bg-white rounded-xl shadow-md overflow-hidden flex flex-col" style={{ height: '500px' }}>
            <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-4 text-white">
              <h3 className="font-bold flex items-center gap-2">
                <MessageCircle className="w-5 h-5" />
                AI 걷기운동 가이드
              </h3>
              <p className="text-sm opacity-90">궁금한 점을 물어보세요</p>
            </div>

            <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
              {messages.map((msg, idx) => (
                <div key={idx} className={`mb-4 flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
                    msg.type === 'user' 
                      ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white' 
                      : 'bg-white shadow-md text-gray-800'
                  }`}>
                    <p className="text-sm whitespace-pre-line">{msg.text}</p>
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="flex justify-start mb-4">
                  <div className="bg-white shadow-md px-4 py-3 rounded-2xl">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="p-4 bg-white border-t flex gap-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="걷기운동에 대해 물어보세요..."
                className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-full focus:outline-none focus:border-purple-500 transition-colors"
              />
              <button
                onClick={handleSend}
                className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-full hover:shadow-lg transition-all flex items-center gap-2 font-medium"
              >
                <Send className="w-4 h-4" />
                전송
              </button>
            </div>
          </div>
        </div>

        {/* Tips Section */}
        <div className="mt-6 bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-6 border-l-4 border-green-500">
          <h3 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
            💡 오늘의 건강 팁
          </h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li>✅ 식후 10-15분 걷기로 혈당 관리를 시작하세요</li>
            <li>✅ 하루 10,000보 목표를 3회로 나눠서 달성해보세요</li>
            <li>✅ 편안한 운동화 착용으로 발 건강을 지키세요</li>
            <li>✅ 걷기 전후 스트레칭으로 부상을 예방하세요</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default WalkingDashboard;
