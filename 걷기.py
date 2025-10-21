import React, { useState, useEffect, useRef } from 'react';
import { Send, Activity, AlertCircle } from 'lucide-react';

const DiabetesWalkingChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [step, setStep] = useState(0);
  const [userData, setUserData] = useState({
    age: null,
    ageGroup: null,
    diabetesType: null,
    activityLevel: null,
    complications: null
  });
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    addBotMessage('안녕하세요! 👋 당뇨병 환자를 위한 걷기운동 가이드 챗봇입니다.');
    setTimeout(() => {
      addBotMessage('맞춤형 걷기운동 권장량을 안내해드리겠습니다. 몇 가지 질문에 답변해주세요.');
      setTimeout(() => {
        addBotMessage('현재 나이를 입력해주세요. (예: 35)');
      }, 800);
    }, 800);
  }, []);

  const addBotMessage = (text, options = null) => {
    setMessages(prev => [...prev, { type: 'bot', text, options }]);
  };

  const addUserMessage = (text) => {
    setMessages(prev => [...prev, { type: 'user', text }]);
  };

  const getAgeGroup = (age) => {
    if (age >= 30 && age < 40) return '30대';
    if (age >= 40 && age < 50) return '40대';
    if (age >= 50 && age < 60) return '50대';
    if (age >= 60) return '60대 이상';
    return null;
  };

  const getRecommendation = () => {
    const recommendations = {
      '30대': {
        steps: '10,000',
        minutes: '30-40',
        intensity: '중강도',
        details: '빠르게 걷기, 약간 숨이 찰 정도의 속도',
        frequency: '주 5회 이상'
      },
      '40대': {
        steps: '10,000',
        minutes: '30-40',
        intensity: '중강도',
        details: '빠르게 걷기, 대화는 가능하지만 노래는 어려운 정도',
        frequency: '주 5회 이상'
      },
      '50대': {
        steps: '8,000-10,000',
        minutes: '25-35',
        intensity: '중강도',
        details: '편안한 속도로 빠르게 걷기',
        frequency: '주 5회 이상'
      },
      '60대 이상': {
        steps: '7,000-8,000',
        minutes: '20-30',
        intensity: '저-중강도',
        details: '편안한 속도로 걷기, 무리하지 않는 범위',
        frequency: '주 5회 이상'
      }
    };

    return recommendations[userData.ageGroup];
  };

  const showFinalRecommendation = () => {
    const rec = getRecommendation();
    
    setTimeout(() => {
      addBotMessage(`📊 ${userData.ageGroup} ${userData.diabetesType} 당뇨병 환자를 위한 걷기운동 권장사항입니다.`);
    }, 500);

    setTimeout(() => {
      addBotMessage(
        `🚶‍♂️ **하루 권장 걸음 수**: ${rec.steps}걸음\n` +
        `⏱️ **하루 권장 시간**: ${rec.minutes}분\n` +
        `💪 **운동 강도**: ${rec.intensity}\n` +
        `📅 **빈도**: ${rec.frequency}\n` +
        `✨ **세부사항**: ${rec.details}`
      );
    }, 1500);

    setTimeout(() => {
      addBotMessage('⚠️ **중요 주의사항**');
    }, 2500);

    setTimeout(() => {
      let warnings = '• 운동 전후 혈당을 측정하세요\n' +
                     '• 저혈당 대비 간식을 준비하세요\n' +
                     '• 편안한 운동화를 착용하세요\n' +
                     '• 발에 물집이나 상처가 없는지 확인하세요';

      if (userData.complications === '있음') {
        warnings += '\n• 합병증이 있으므로 반드시 담당 의사와 상담 후 운동하세요\n' +
                   '• 처음에는 더 짧은 시간부터 시작하세요';
      }

      if (userData.activityLevel === '거의 안함') {
        warnings += '\n• 현재 활동량이 적으므로 권장량의 50%부터 시작하세요\n' +
                   '• 2-4주에 걸쳐 점진적으로 늘려가세요';
      }

      addBotMessage(warnings);
    }, 3500);

    setTimeout(() => {
      addBotMessage('💡 **추가 팁**\n' +
                   '• 식후 1-2시간 후 걷기가 혈당 조절에 효과적입니다\n' +
                   '• 걷기를 여러 번 나누어 해도 좋습니다 (예: 10분씩 3회)\n' +
                   '• 만보계나 스마트폰 앱을 활용해 걸음 수를 기록하세요');
    }, 4500);

    setTimeout(() => {
      addBotMessage('⚕️ 본 권장사항은 일반적인 가이드라인이며, 개인의 건강 상태에 따라 다를 수 있습니다. 운동 프로그램 시작 전 반드시 담당 의사와 상담하세요.');
    }, 5500);

    setTimeout(() => {
      addBotMessage('다시 상담하시려면 페이지를 새로고침해주세요. 😊', [
        { label: '새로 시작하기', value: 'restart' }
      ]);
      setStep(6);
    }, 6500);
  };

  const handleSend = () => {
    if (!input.trim()) return;

    const userInput = input.trim();
    addUserMessage(userInput);
    setInput('');

    setTimeout(() => {
      processInput(userInput);
    }, 500);
  };

  const handleOptionClick = (value) => {
    addUserMessage(value);
    
    setTimeout(() => {
      processInput(value);
    }, 500);
  };

  const processInput = (userInput) => {
    switch(step) {
      case 0: // 나이 입력
        const age = parseInt(userInput);
        if (isNaN(age) || age < 30 || age > 100) {
          addBotMessage('30세 이상의 올바른 나이를 입력해주세요.');
          return;
        }
        const ageGroup = getAgeGroup(age);
        setUserData(prev => ({ ...prev, age, ageGroup }));
        addBotMessage(`${ageGroup}시군요. 당뇨병 유형을 선택해주세요.`, [
          { label: '1형 당뇨병', value: '1형' },
          { label: '2형 당뇨병', value: '2형' }
        ]);
        setStep(1);
        break;

      case 1: // 당뇨병 타입
        if (userInput !== '1형' && userInput !== '2형') {
          addBotMessage('1형 또는 2형을 선택해주세요.');
          return;
        }
        setUserData(prev => ({ ...prev, diabetesType: userInput }));
        addBotMessage('현재 평소 활동 수준은 어떠신가요?', [
          { label: '거의 안함', value: '거의 안함' },
          { label: '가끔 (주 1-2회)', value: '가끔' },
          { label: '자주 (주 3-4회)', value: '자주' },
          { label: '매우 자주 (주 5회 이상)', value: '매우 자주' }
        ]);
        setStep(2);
        break;

      case 2: // 활동 수준
        setUserData(prev => ({ ...prev, activityLevel: userInput }));
        addBotMessage('당뇨 합병증(신장, 망막, 신경병증 등)이 있으신가요?', [
          { label: '없음', value: '없음' },
          { label: '있음', value: '있음' }
        ]);
        setStep(3);
        break;

      case 3: // 합병증
        setUserData(prev => ({ ...prev, complications: userInput }));
        addBotMessage('정보를 분석하고 있습니다... 잠시만 기다려주세요. ⏳');
        setStep(4);
        showFinalRecommendation();
        break;

      case 6: // 재시작
        if (userInput === '새로 시작하기' || userInput === 'restart') {
          window.location.reload();
        }
        break;

      default:
        break;
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-md p-4 flex items-center gap-3">
        <Activity className="text-indigo-600" size={28} />
        <div>
          <h1 className="text-xl font-bold text-gray-800">당뇨병 환자 걷기운동 가이드</h1>
          <p className="text-sm text-gray-600">맞춤형 운동량 추천 챗봇</p>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] ${msg.type === 'user' ? 'bg-indigo-600 text-white' : 'bg-white text-gray-800'} rounded-2xl px-4 py-3 shadow-md`}>
              <div className="whitespace-pre-line">{msg.text}</div>
              {msg.options && (
                <div className="mt-3 space-y-2">
                  {msg.options.map((option, i) => (
                    <button
                      key={i}
                      onClick={() => handleOptionClick(option.value)}
                      className="block w-full text-left px-4 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-lg transition-colors duration-200 font-medium"
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Disclaimer */}
      <div className="bg-yellow-50 border-t border-yellow-200 p-3 flex items-start gap-2">
        <AlertCircle className="text-yellow-600 flex-shrink-0 mt-0.5" size={18} />
        <p className="text-xs text-yellow-800">
          본 챗봇은 일반적인 정보 제공 목적이며, 의학적 조언을 대체하지 않습니다. 운동 시작 전 반드시 의사와 상담하세요.
        </p>
      </div>

      {/* Input Area */}
      {step < 6 && (
        <div className="bg-white border-t border-gray-200 p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="메시지를 입력하세요..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              disabled={step === 4 || step === 5}
            />
            <button
              onClick={handleSend}
              disabled={step === 4 || step === 5}
              className="bg-indigo-600 text-white p-3 rounded-full hover:bg-indigo-700 transition-colors duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DiabetesWalkingChatbot;
