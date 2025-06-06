import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import './App.css';

const App = () => {
  const [currentPage, setCurrentPage] = useState('landing');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Auth states
  const [authMode, setAuthMode] = useState('login');
  const [authData, setAuthData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    age: '',
    studentLevel: '',
    consentGiven: false
  });

  // DASS-21 states
  const [dassResponses, setDassResponses] = useState({});
  const [dassResults, setDassResults] = useState(null);

  // Mood tracker states
  const [todayMood, setTodayMood] = useState(null);
  const [moodNote, setMoodNote] = useState('');
  const [moodHistory, setMoodHistory] = useState([]);
  const [assessmentHistory, setAssessmentHistory] = useState([]);

  // Chatbot states
  const [chatMessages, setChatMessages] = useState([
    { sender: 'bot', text: 'سلام! من دستیار سلامت روان شما هستم. امروز چطور احساس می‌کنید؟', time: new Date() }
  ]);
  const [chatInput, setChatInput] = useState('');

  // PHQ-9 states
  const [phqResponses, setPhqResponses] = useState({});
  const [phqResults, setPhqResults] = useState(null);

  // Mental health plan state
  const [userPlan, setUserPlan] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchUserProfile(token);
    }
  }, []);

  const fetchUserProfile = async (token) => {
    try {
      const response = await axios.get(`${backendUrl}/api/profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
      setCurrentPage('dashboard');
      fetchUserData();
    } catch (error) {
      localStorage.removeItem('token');
    }
  };

  const fetchUserData = async () => {
    try {
      const token = localStorage.getItem('token');
      // Fetch mood data
      const moodResponse = await axios.get(`${backendUrl}/api/mood-entries`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMoodHistory(moodResponse.data);

      // Check today's mood
      const today = new Date().toISOString().split('T')[0];
      const todayEntry = moodResponse.data.find(entry => 
        entry.date.split('T')[0] === today
      );
      if (todayEntry) {
        setTodayMood(todayEntry.mood_level);
        setMoodNote(todayEntry.note || '');
      }

      // Fetch mental health plan
      const planResponse = await axios.get(`${backendUrl}/api/mental-health-plan`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUserPlan(planResponse.data);

      // Fetch recent assessments
      const assessResponse = await axios.get(`${backendUrl}/api/assessments`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAssessmentHistory(assessResponse.data);
    } catch (error) {
      console.log('Error fetching user data:', error);
    }
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const endpoint = authMode === 'login' ? '/api/login' : '/api/register';
      const payload = authMode === 'login' 
        ? { email: authData.email, password: authData.password }
        : authData;

      const response = await axios.post(`${backendUrl}${endpoint}`, payload);
      
      localStorage.setItem('token', response.data.access_token);
      setUser(response.data.user);
      setCurrentPage('dashboard');
      fetchUserData();
    } catch (error) {
      setError(error.response?.data?.detail || 'خطایی رخ داده است');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setCurrentPage('landing');
    setAuthData({
      email: '',
      password: '',
      confirmPassword: '',
      fullName: '',
      age: '',
      studentLevel: '',
      consentGiven: false
    });
    // Reset all state
    setMoodHistory([]);
    setTodayMood(null);
    setChatMessages([
      { sender: 'bot', text: 'سلام! من دستیار سلامت روان شما هستم. امروز چطور احساس می‌کنید؟', time: new Date() }
    ]);
    setUserPlan(null);
    setAssessmentHistory([]);
  };

  const saveMoodEntry = async () => {
    if (!todayMood) return;
    
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${backendUrl}/api/mood-entry`, {
        mood_level: todayMood,
        note: moodNote
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchUserData();
      setCurrentPage('dashboard');
    } catch (error) {
      setError('خطا در ذخیره خلق و خو');
    } finally {
      setLoading(false);
    }
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim()) return;

    const userMessage = {
      sender: 'user',
      text: chatInput,
      time: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${backendUrl}/api/chat`, {
        message: chatInput
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const botMessage = {
        sender: 'bot',
        text: response.data.response,
        time: new Date()
      };

      setChatMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        sender: 'bot',
        text: 'متأسفم، در حال حاضر مشکلی در ارتباط دارم. لطفاً دوباره تلاش کنید.',
        time: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    }
  };

  const dass21Questions = [
    { id: 1, text: "در گذشته یک هفته، من سخت بیان احساساتم کردم", category: "depression" },
    { id: 2, text: "در گذشته یک هفته، من شرایطی را تجربه کردم که باعث خشکی دهانم شد", category: "anxiety" },
    { id: 3, text: "در گذشته یک هفته، نتوانستم احساس مثبتی داشته باشم", category: "depression" },
    { id: 4, text: "در گذشته یک هفته، مشکل تنفسی داشتم", category: "anxiety" },
    { id: 5, text: "در گذشته یک هفته، سخت ابتکار عمل پیدا کردم", category: "depression" },
    { id: 6, text: "در گذشته یک هفته، تمایل داشتم روی موقعیت‌ها بیش از حد واکنش نشان دهم", category: "stress" },
    { id: 7, text: "در گذشته یک هفته، لرزش داشتم", category: "anxiety" },
    { id: 8, text: "در گذشته یک هفته، احساس کردم انرژی زیادی صرف کرده‌ام", category: "stress" },
    { id: 9, text: "در گذشته یک هفته، نگران موقعیت‌هایی بودم که ممکن است پانیک کنم", category: "anxiety" },
    { id: 10, text: "در گذشته یک هفته، احساس کردم چیزی برای لذت بردن ندارم", category: "depression" },
    { id: 11, text: "در گذشته یک هفته، خودم را آشفته دیدم", category: "stress" },
    { id: 12, text: "در گذشته یک هفته، سخت آرام شدم", category: "stress" },
    { id: 13, text: "در گذشته یک هفته، غمگین و افسرده بودم", category: "depression" },
    { id: 14, text: "در گذشته یک هفته، نسبت به هر چیزی که مرا از ادامه کاری که انجام می‌دادم باز می‌داشت بی‌تابی کردم", category: "stress" },
    { id: 15, text: "در گذشته یک هفته، احساس ترس کردم", category: "anxiety" },
    { id: 16, text: "در گذشته یک هفته، احساس کردم آینده‌ای ندارم", category: "depression" },
    { id: 17, text: "در گذشته یک هفته، احساس کردم زندگی بی‌معناست", category: "depression" },
    { id: 18, text: "در گذشته یک هفته، تحریک‌پذیر بودم", category: "stress" },
    { id: 19, text: "در گذشته یک هفته، تپش قلب داشتم", category: "anxiety" },
    { id: 20, text: "در گذشته یک هفته، بدون دلیل مشخص ترسیدم", category: "anxiety" },
    { id: 21, text: "در گذشته یک هفته، احساس کردم زندگی ارزشی ندارد", category: "depression" }
  ];

  const phq9Questions = [
    { id: 1, text: "علاقه کم یا عدم لذت بردن از انجام کارها" },
    { id: 2, text: "احساس غمگینی، افسردگی یا ناامیدی" },
    { id: 3, text: "مشکل در به خواب رفتن، خواب ماندن یا خواب زیاد" },
    { id: 4, text: "احساس خستگی یا کم انرژی بودن" },
    { id: 5, text: "اشتهای کم یا پرخوری" },
    { id: 6, text: "احساس بدی نسبت به خودتان - یا اینکه شکست خورده‌اید یا خود و خانواده‌تان را ناامید کرده‌اید" },
    { id: 7, text: "مشکل در تمرکز روی چیزهایی مثل خواندن روزنامه یا تماشای تلویزیون" },
    { id: 8, text: "حرکت یا صحبت کردن آنقدر کند که دیگران متوجه شوند؟ یا برعکس - بی‌قراری یا پریشانی شدید" },
    { id: 9, text: "افکار مرگ یا آسیب رساندن به خود" }
  ];

  const submitDASS21 = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${backendUrl}/api/submit-dass21`, 
        { responses: dassResponses },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      setDassResults(response.data);
      setCurrentPage('results');
    } catch (error) {
      setError('خطا در ارسال پاسخ‌ها');
    } finally {
      setLoading(false);
    }
  };

  const submitPHQ9 = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${backendUrl}/api/submit-phq9`, 
        { responses: phqResponses },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      setPhqResults(response.data);
      setCurrentPage('phq-results');
    } catch (error) {
      setError('خطا در ارسال پاسخ‌ها');
    } finally {
      setLoading(false);
    }
  };

  const ConsentForm = () => (
    <div className="bg-white rounded-lg p-8 shadow-lg max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-right text-gray-800 mb-6">فرم رضایت‌نامه</h2>
      <div className="text-right text-gray-700 space-y-4 mb-6">
        <p>با شرکت در این مطالعه:</p>
        <ul className="list-disc list-inside space-y-2">
          <li>موافقت می‌کنم که اطلاعات من برای اهداف تحقیقاتی استفاده شود</li>
          <li>می‌دانم که اطلاعات من محرمانه نگهداری می‌شود</li>
          <li>آگاهم که این ابزار جایگزین مشاوره پزشکی نیست</li>
          <li>می‌توانم هر زمان از مطالعه خارج شوم</li>
          <li>می‌دانم که داده‌های من به صورت ناشناس در تحقیق استفاده می‌شود</li>
        </ul>
      </div>
      <label className="flex items-center text-right">
        <span className="mr-3">موافقت می‌کنم</span>
        <input
          type="checkbox"
          checked={authData.consentGiven}
          onChange={(e) => setAuthData({...authData, consentGiven: e.target.checked})}
          className="mr-2"
        />
      </label>
    </div>
  );

  const AuthForm = () => (
    <div className="bg-white rounded-lg p-8 shadow-lg max-w-md mx-auto">
      <h2 className="text-2xl font-bold text-right text-gray-800 mb-6">
        {authMode === 'login' ? 'ورود' : 'ثبت‌نام'}
      </h2>
      
      <form onSubmit={handleAuth} className="space-y-4">
        {authMode === 'register' && (
          <>
            <input
              type="text"
              placeholder="نام کامل"
              value={authData.fullName}
              onChange={(e) => setAuthData({...authData, fullName: e.target.value})}
              className="w-full p-3 border rounded-lg text-right"
              required
            />
            <input
              type="number"
              placeholder="سن"
              value={authData.age}
              onChange={(e) => setAuthData({...authData, age: e.target.value})}
              className="w-full p-3 border rounded-lg text-right"
              required
            />
            <select
              value={authData.studentLevel}
              onChange={(e) => setAuthData({...authData, studentLevel: e.target.value})}
              className="w-full p-3 border rounded-lg text-right cursor-pointer"
              required
            >
              <option value="" disabled>سطح تحصیلات</option>
              <option value="undergraduate">کارشناسی</option>
              <option value="master">کارشناسی ارشد</option>
              <option value="phd">دکتری</option>
            </select>
          </>
        )}
        
        <input
          type="email"
          placeholder="ایمیل"
          value={authData.email}
          onChange={(e) => setAuthData({...authData, email: e.target.value})}
          className="w-full p-3 border rounded-lg text-right"
          required
        />
        
        <input
          type="password"
          placeholder="رمز عبور"
          value={authData.password}
          onChange={(e) => setAuthData({...authData, password: e.target.value})}
          className="w-full p-3 border rounded-lg text-right"
          required
        />
        
        {authMode === 'register' && (
          <input
            type="password"
            placeholder="تکرار رمز عبور"
            value={authData.confirmPassword}
            onChange={(e) => setAuthData({...authData, confirmPassword: e.target.value})}
            className="w-full p-3 border rounded-lg text-right"
            required
          />
        )}
        
        {error && <p className="text-red-500 text-right">{error}</p>}
        
        <button
          type="submit"
          disabled={loading || (authMode === 'register' && !authData.consentGiven)}
          className="w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'در حال پردازش...' : authMode === 'login' ? 'ورود' : 'ثبت‌نام'}
        </button>
      </form>
      
      <p className="text-center mt-4">
        {authMode === 'login' ? 'حساب کاربری ندارید؟' : 'حساب کاربری دارید؟'}
        <button
          onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
          className="text-blue-600 mr-2"
        >
          {authMode === 'login' ? 'ثبت‌نام' : 'ورود'}
        </button>
      </p>
    </div>
  );

  const Dashboard = () => (
    <div className="bg-white rounded-lg p-8 shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <button
          onClick={handleLogout}
          className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        >
          خروج
        </button>
        <h2 className="text-2xl font-bold text-right">خوش آمدید، {user?.full_name}</h2>
      </div>

      {/* Today's mood status */}
      {todayMood && (
        <div className="mb-6 p-4 bg-green-50 rounded-lg border-right-4 border-green-500">
          <p className="text-right text-green-800">
            خلق و خوی امروز شما: {getMoodText(todayMood)} ثبت شده است
          </p>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          onClick={() => setCurrentPage('dass21')}
          className="bg-gradient-to-br from-blue-500 to-purple-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg transition-shadow"
        >
          <h3 className="text-xl font-bold text-right mb-2">آزمون DASS-21</h3>
          <p className="text-right opacity-90">ارزیابی افسردگی، اضطراب و استرس</p>
        </div>
        
        <div 
          onClick={() => setCurrentPage('phq9')}
          className="bg-gradient-to-br from-indigo-500 to-blue-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg transition-shadow"
        >
          <h3 className="text-xl font-bold text-right mb-2">آزمون PHQ-9</h3>
          <p className="text-right opacity-90">ارزیابی تخصصی افسردگی</p>
        </div>
        
        <div 
          onClick={() => setCurrentPage('mood-tracker')}
          className="bg-gradient-to-br from-green-500 to-teal-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg transition-shadow"
        >
          <h3 className="text-xl font-bold text-right mb-2">ثبت خلق و خو روزانه</h3>
          <p className="text-right opacity-90">امروز چطور احساس می‌کنید؟</p>
        </div>
        
        <div 
          onClick={() => setCurrentPage('chatbot')}
          className="bg-gradient-to-br from-orange-500 to-red-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg transition-shadow"
        >
          <h3 className="text-xl font-bold text-right mb-2">گپ با مشاور</h3>
          <p className="text-right opacity-90">صحبت کردن می‌تواند کمک کند</p>
        </div>
        
        <div 
          onClick={() => setCurrentPage('mental-health-plan')}
          className="bg-gradient-to-br from-purple-500 to-pink-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg transition-shadow"
        >
          <h3 className="text-xl font-bold text-right mb-2">نقشه راه سلامت روان</h3>
          <p className="text-right opacity-90">برنامه شخصی‌سازی شده برای بهبود</p>
        </div>

        <div
          onClick={() => setCurrentPage('history')}
          className="bg-gradient-to-br from-gray-500 to-gray-700 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg transition-shadow"
        >
          <h3 className="text-xl font-bold text-right mb-2">تاریخچه ارزیابی‌ها</h3>
          <p className="text-right opacity-90">مشاهده نتایج قبلی</p>
        </div>
      </div>

      {/* Charts Section */}
      {moodHistory.length > 0 && (
        <div className="mt-10">
          <h3 className="text-xl font-bold mb-4 text-right">روند خلق و خو</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart
              data={moodHistory
                .slice()
                .reverse()
                .map((entry) => ({
                  date: new Date(entry.date).toLocaleDateString('fa-IR'),
                  mood: entry.mood_level,
                }))}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[1, 5]} allowDecimals={false} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="mood" stroke="#8884d8" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {assessmentHistory.some((a) => a.assessment_type === 'DASS-21') && (
        <div className="mt-10">
          <h3 className="text-xl font-bold mb-4 text-right">آخرین نتیجه DASS-21</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={(function () {
                const latest = assessmentHistory.find(
                  (a) => a.assessment_type === 'DASS-21'
                );
                if (!latest) return [];
                return [
                  {
                    name: 'افسردگی',
                    score: latest.results.depression_score,
                  },
                  {
                    name: 'اضطراب',
                    score: latest.results.anxiety_score,
                  },
                  {
                    name: 'استرس',
                    score: latest.results.stress_score,
                  },
                ];
              })()}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 42]} />
              <Tooltip />
              <Legend />
              <Bar dataKey="score" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );

  const MoodTracker = () => {
    const moodOptions = [
      { value: 5, emoji: '😊', label: 'عالی', color: 'text-green-600' },
      { value: 4, emoji: '🙂', label: 'خوب', color: 'text-green-400' },
      { value: 3, emoji: '😐', label: 'متوسط', color: 'text-yellow-500' },
      { value: 2, emoji: '🙁', label: 'بد', color: 'text-orange-500' },
      { value: 1, emoji: '😢', label: 'خیلی بد', color: 'text-red-500' }
    ];

    return (
      <div className="bg-white rounded-lg p-8 shadow-lg max-w-2xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <button
            onClick={() => setCurrentPage('dashboard')}
            className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
          >
            بازگشت
          </button>
          <h2 className="text-2xl font-bold text-right">ثبت خلق و خو روزانه</h2>
        </div>

        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-right mb-4">امروز چطور احساس می‌کنید؟</h3>
            <div className="grid grid-cols-1 gap-3">
              {moodOptions.map((mood) => (
                <label 
                  key={mood.value}
                  className={`flex items-center justify-end p-4 border rounded-lg cursor-pointer hover:bg-gray-50 ${
                    todayMood === mood.value ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                  }`}
                >
                  <span className="mr-3 text-right">
                    <span className={`font-semibold ${mood.color}`}>{mood.label}</span>
                  </span>
                  <span className="text-2xl mr-3">{mood.emoji}</span>
                  <input
                    type="radio"
                    name="mood"
                    value={mood.value}
                    checked={todayMood === mood.value}
                    onChange={(e) => setTodayMood(parseInt(e.target.value))}
                    className="ml-3"
                  />
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-right text-lg font-semibold mb-2">
              یادداشت (اختیاری):
            </label>
            <textarea
              value={moodNote}
              onChange={(e) => setMoodNote(e.target.value)}
              placeholder="چه چیزی باعث این احساس شده؟ چه اتفاقی افتاده؟"
              className="w-full p-3 border rounded-lg text-right resize-none"
              rows="4"
            />
          </div>

          <button
            onClick={saveMoodEntry}
            disabled={!todayMood || loading}
            className="w-full bg-green-600 text-white p-3 rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {loading ? 'در حال ذخیره...' : 'ذخیره خلق و خو امروز'}
          </button>
        </div>

        {/* Recent mood history */}
        {moodHistory.length > 0 && (
          <div className="mt-8">
            <h3 className="text-lg font-semibold text-right mb-4">روزهای اخیر:</h3>
            <div className="space-y-2">
              {moodHistory.slice(0, 7).map((entry, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span className="text-sm text-gray-600">
                    {new Date(entry.date).toLocaleDateString('fa-IR')}
                  </span>
                  <span className="flex items-center">
                    <span className="mr-2">{getMoodText(entry.mood_level)}</span>
                    <span className="text-xl">{getMoodEmoji(entry.mood_level)}</span>
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const Chatbot = () => (
    <div className="bg-white rounded-lg p-6 shadow-lg max-w-4xl mx-auto h-[600px] flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <button
          onClick={() => setCurrentPage('dashboard')}
          className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
        >
          بازگشت
        </button>
        <h2 className="text-2xl font-bold text-right">مشاور هوشمند</h2>
      </div>

      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto border rounded-lg p-4 mb-4 space-y-4">
        {chatMessages.map((message, index) => (
          <div key={index} className={`flex ${message.sender === 'user' ? 'justify-start' : 'justify-end'}`}>
            <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
              message.sender === 'user' 
                ? 'bg-blue-500 text-white chat-bubble-user' 
                : 'bg-gray-200 text-gray-800 chat-bubble-bot'
            }`}>
              <p className="text-right">{message.text}</p>
              <p className={`text-xs mt-1 ${message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                {message.time.toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Chat input */}
      <div className="flex gap-2">
        <button
          onClick={sendChatMessage}
          disabled={!chatInput.trim()}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          ارسال
        </button>
        <input
          type="text"
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
          placeholder="پیام خود را بنویسید..."
          className="flex-1 p-2 border rounded-lg text-right"
        />
      </div>
    </div>
  );

  const PHQ9Test = () => (
    <div className="bg-white rounded-lg p-8 shadow-lg max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <button
          onClick={() => setCurrentPage('dashboard')}
          className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
        >
          بازگشت
        </button>
        <h2 className="text-2xl font-bold text-right">آزمون PHQ-9</h2>
      </div>
      
      <p className="text-right text-gray-600 mb-6">
        در دو هفته گذشته، کدام یک از مشکلات زیر چقدر شما را آزار داده است؟
      </p>
      
      <div className="space-y-6">
        {phq9Questions.map((question) => (
          <div key={question.id} className="border-b pb-4">
            <p className="text-right font-medium mb-3">{question.text}</p>
            <div className="flex justify-end space-x-4 space-x-reverse">
              {[
                { value: 0, label: 'اصلاً' },
                { value: 1, label: 'چند روز' },
                { value: 2, label: 'بیش از نیمی از روزها' },
                { value: 3, label: 'تقریباً هر روز' }
              ].map((option) => (
                <label key={option.value} className="flex items-center cursor-pointer">
                  <span className="mr-2 text-sm">{option.label}</span>
                  <input
                    type="radio"
                    name={`phq_question_${question.id}`}
                    value={option.value}
                    checked={phqResponses[question.id] === option.value}
                    onChange={(e) => setPhqResponses({
                      ...phqResponses,
                      [question.id]: parseInt(e.target.value)
                    })}
                    className="mr-1 cursor-pointer"
                  />
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-8 text-center">
        <button
          onClick={submitPHQ9}
          disabled={loading || Object.keys(phqResponses).length !== 9}
          className="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? 'در حال پردازش...' : 'ارسال و دریافت نتایج'}
        </button>
      </div>
    </div>
  );

  const DASS21Test = () => (
    <div className="bg-white rounded-lg p-8 shadow-lg max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <button
          onClick={() => setCurrentPage('dashboard')}
          className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
        >
          بازگشت
        </button>
        <h2 className="text-2xl font-bold text-right">آزمون DASS-21</h2>
      </div>
      
      <p className="text-right text-gray-600 mb-6">
        لطفاً هر سوال را با دقت بخوانید و بر اساس تجربه شما در هفته گذشته پاسخ دهید.
      </p>
      
      <div className="space-y-6">
        {dass21Questions.map((question) => (
          <div key={question.id} className="border-b pb-4">
            <p className="text-right font-medium mb-3">{question.text}</p>
            <div className="flex justify-end space-x-4 space-x-reverse">
              {[
                { value: 0, label: 'اصلاً' },
                { value: 1, label: 'گاهی' },
                { value: 2, label: 'اغلب' },
                { value: 3, label: 'خیلی زیاد' }
              ].map((option) => (
                <label key={option.value} className="flex items-center cursor-pointer">
                  <span className="mr-2 text-sm">{option.label}</span>
                  <input
                    type="radio"
                    name={`question_${question.id}`}
                    value={option.value}
                    checked={dassResponses[question.id] === option.value}
                    onChange={(e) => setDassResponses({
                      ...dassResponses,
                      [question.id]: parseInt(e.target.value)
                    })}
                    className="mr-1 cursor-pointer"
                  />
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-8 text-center">
        <button
          onClick={submitDASS21}
          disabled={loading || Object.keys(dassResponses).length !== 21}
          className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'در حال پردازش...' : 'ارسال و دریافت نتایج'}
        </button>
      </div>
    </div>
  );

  const Results = () => (
    <div className="bg-white rounded-lg p-8 shadow-lg max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <button
          onClick={() => setCurrentPage('dashboard')}
          className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
        >
          بازگشت به داشبورد
        </button>
        <h2 className="text-2xl font-bold text-right">نتایج آزمون DASS-21</h2>
      </div>
      
      {dassResults && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-blue-50 p-6 rounded-lg">
              <h3 className="text-xl font-bold text-right text-blue-800 mb-2">افسردگی</h3>
              <p className="text-3xl font-bold text-right text-blue-600">{dassResults.depression_score}</p>
              <p className="text-right text-blue-700">{dassResults.depression_level}</p>
            </div>
            
            <div className="bg-orange-50 p-6 rounded-lg">
              <h3 className="text-xl font-bold text-right text-orange-800 mb-2">اضطراب</h3>
              <p className="text-3xl font-bold text-right text-orange-600">{dassResults.anxiety_score}</p>
              <p className="text-right text-orange-700">{dassResults.anxiety_level}</p>
            </div>
            
            <div className="bg-red-50 p-6 rounded-lg">
              <h3 className="text-xl font-bold text-right text-red-800 mb-2">استرس</h3>
              <p className="text-3xl font-bold text-right text-red-600">{dassResults.stress_score}</p>
              <p className="text-right text-red-700">{dassResults.stress_level}</p>
            </div>
          </div>
          
          <div className="bg-green-50 p-6 rounded-lg">
            <h3 className="text-xl font-bold text-right text-green-800 mb-4">تجزیه و تحلیل هوش مصنوعی</h3>
            <p className="text-right text-green-700">{dassResults.ai_analysis}</p>
          </div>
          
          <div className="bg-purple-50 p-6 rounded-lg">
            <h3 className="text-xl font-bold text-right text-purple-800 mb-4">پیشنهادات</h3>
            <ul className="text-right text-purple-700 space-y-2">
              {dassResults.recommendations?.map((rec, index) => (
                <li key={index} className="flex items-start">
                  <span className="ml-2">•</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );

  const PHQResults = () => (
    <div className="bg-white rounded-lg p-8 shadow-lg max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <button
          onClick={() => setCurrentPage('dashboard')}
          className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
        >
          بازگشت به داشبورد
        </button>
        <h2 className="text-2xl font-bold text-right">نتایج آزمون PHQ-9</h2>
      </div>
      
      {phqResults && (
        <div className="space-y-6">
          <div className="bg-indigo-50 p-6 rounded-lg text-center">
            <h3 className="text-2xl font-bold text-right text-indigo-800 mb-2">امتیاز کل افسردگی</h3>
            <p className="text-4xl font-bold text-right text-indigo-600 mb-2">{phqResults.total_score}</p>
            <p className="text-xl text-right text-indigo-700">{phqResults.severity_level}</p>
          </div>
          
          <div className="bg-green-50 p-6 rounded-lg">
            <h3 className="text-xl font-bold text-right text-green-800 mb-4">تجزیه و تحلیل</h3>
            <p className="text-right text-green-700">{phqResults.analysis}</p>
          </div>
          
          <div className="bg-blue-50 p-6 rounded-lg">
            <h3 className="text-xl font-bold text-right text-blue-800 mb-4">پیشنهادات</h3>
            <ul className="text-right text-blue-700 space-y-2">
              {phqResults.recommendations?.map((rec, index) => (
                <li key={index} className="flex items-start">
                  <span className="ml-2">•</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );

  const MentalHealthPlan = () => (
    <div className="bg-white rounded-lg p-8 shadow-lg max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <button
          onClick={() => setCurrentPage('dashboard')}
          className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
        >
          بازگشت
        </button>
        <h2 className="text-2xl font-bold text-right">نقشه راه سلامت روان</h2>
      </div>

      <div className="space-y-6">
        {/* Daily habits */}
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-lg">
          <h3 className="text-xl font-bold text-right text-purple-800 mb-4">عادات روزانه پیشنهادی</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              '۱۰ دقیقه تنفس عمیق صبحگاهی',
              '۳۰ دقیقه پیاده‌روی در طبیعت',
              'نوشتن ۳ چیز مثبت روز در دفترچه',
              'مدیتیشن ۵ دقیقه‌ای قبل خواب',
              'محدود کردن رسانه‌های اجتماعی',
              'خواب منظم ۷-۸ ساعته'
            ].map((habit, index) => (
              <div key={index} className="flex items-center bg-white p-3 rounded shadow-sm">
                <span className="text-right flex-1">{habit}</span>
                <span className="text-green-500 mr-2">✓</span>
              </div>
            ))}
          </div>
        </div>

        {/* Weekly goals */}
        <div className="bg-gradient-to-r from-blue-50 to-cyan-50 p-6 rounded-lg">
          <h3 className="text-xl font-bold text-right text-blue-800 mb-4">اهداف هفتگی</h3>
          <div className="space-y-3">
            {[
              'شرکت در یک فعالیت اجتماعی',
              'یادگیری یک مهارت جدید (۱ ساعت)',
              'ارتباط با دوست یا خانواده',
              'انجام یک کار داوطلبانه کوچک'
            ].map((goal, index) => (
              <div key={index} className="bg-white p-4 rounded shadow-sm">
                <span className="text-right block">{goal}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Emergency resources */}
        <div className="bg-gradient-to-r from-red-50 to-orange-50 p-6 rounded-lg">
          <h3 className="text-xl font-bold text-right text-red-800 mb-4">منابع اورژانسی</h3>
          <div className="space-y-2 text-right">
            <p><strong>خط کمک اورژانس:</strong> ۱۱۵</p>
            <p><strong>مرکز بحران سلامت روان:</strong> ۱۴۸۰</p>
            <p><strong>در مواقع اضطراری فوری:</strong> ۱۱۰</p>
            <p className="text-red-600 font-semibold">
              در صورت داشتن افکار آسیب‌رسانی، فوراً با این شماره‌ها تماس بگیرید.
            </p>
          </div>
        </div>

        {/* CBT techniques */}
        <div className="bg-gradient-to-r from-green-50 to-teal-50 p-6 rounded-lg">
          <h3 className="text-xl font-bold text-right text-green-800 mb-4">تکنیک‌های درمان شناختی-رفتاری</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { title: 'تنفس ۴-۷-۸', desc: '۴ ثانیه نفس بکشید، ۷ ثانیه نگه دارید، ۸ ثانیه بدهید' },
              { title: 'تکنیک ۵-۴-۳-۲-۱', desc: '۵ چیز ببینید، ۴ چیز لمس کنید، ۳ صدا بشنوید، ۲ بو استشمام کنید، ۱ طعم بچشید' },
              { title: 'سوال از افکار منفی', desc: 'آیا این فکر واقعی است؟ شواهد چیست؟' },
              { title: 'برنامه‌ریزی فعالیت', desc: 'کارهای لذت‌بخش و معنادار را برنامه‌ریزی کنید' }
            ].map((technique, index) => (
              <div key={index} className="bg-white p-4 rounded shadow-sm">
                <h4 className="font-bold text-right text-green-700 mb-2">{technique.title}</h4>
                <p className="text-right text-gray-600 text-sm">{technique.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const History = () => (
    <div className="bg-white rounded-lg p-8 shadow-lg max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <button
          onClick={() => setCurrentPage('dashboard')}
          className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
        >
          بازگشت
        </button>
        <h2 className="text-2xl font-bold text-right">تاریخچه ارزیابی‌ها</h2>
      </div>
      
      <div className="text-center py-8">
        <p className="text-gray-600">این بخش به زودی اضافه خواهد شد...</p>
        <p className="text-gray-500 text-sm mt-2">تاریخچه آزمون‌ها و پیشرفت شما در اینجا نمایش داده خواهد شد</p>
      </div>
    </div>
  );

  const LandingPage = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-800 mb-4">
            سلامت روان دانشجویان
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            ابزار هوشمند ارزیابی و پشتیبانی سلامت روان برای دانشجویان ایرانی
          </p>
        </div>
        
        <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <div className="bg-white rounded-lg p-6 shadow-lg text-center">
            <div className="text-4xl mb-4">🧠</div>
            <h3 className="text-xl font-bold mb-2">ارزیابی علمی</h3>
            <p className="text-gray-600">آزمون‌های معتبر روان‌شناختی با تحلیل هوش مصنوعی</p>
          </div>
          
          <div className="bg-white rounded-lg p-6 shadow-lg text-center">
            <div className="text-4xl mb-4">💬</div>
            <h3 className="text-xl font-bold mb-2">مشاوره آنلاین</h3>
            <p className="text-gray-600">چت هوشمند برای پشتیبانی روزانه و راهنمایی</p>
          </div>
          
          <div className="bg-white rounded-lg p-6 shadow-lg text-center">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-bold mb-2">پیگیری مداوم</h3>
            <p className="text-gray-600">ثبت خلق و خو روزانه و برنامه بهبود شخصی</p>
          </div>
        </div>
        
        <div className="text-center">
          <button
            onClick={() => setCurrentPage('auth')}
            className="bg-blue-600 text-white px-8 py-4 rounded-lg text-xl hover:bg-blue-700 transition-colors"
          >
            شروع کنید
          </button>
        </div>
      </div>
    </div>
  );

  // Helper functions
  const getMoodText = (mood) => {
    const moodMap = {
      1: 'خیلی بد',
      2: 'بد', 
      3: 'متوسط',
      4: 'خوب',
      5: 'عالی'
    };
    return moodMap[mood] || 'نامشخص';
  };

  const getMoodEmoji = (mood) => {
    const emojiMap = {
      1: '😢',
      2: '🙁',
      3: '😐', 
      4: '🙂',
      5: '😊'
    };
    return emojiMap[mood] || '❓';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50" dir="rtl">
      <div className="container mx-auto px-4 py-8">
        {currentPage === 'landing' && <LandingPage />}
        {currentPage === 'auth' && (
          <div className="space-y-8">
            {authMode === 'register' && <ConsentForm />}
            <AuthForm />
          </div>
        )}
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'dass21' && <DASS21Test />}
        {currentPage === 'phq9' && <PHQ9Test />}
        {currentPage === 'mood-tracker' && <MoodTracker />}
        {currentPage === 'chatbot' && <Chatbot />}
        {currentPage === 'mental-health-plan' && <MentalHealthPlan />}
        {currentPage === 'history' && <History />}
        {currentPage === 'results' && <Results />}
        {currentPage === 'phq-results' && <PHQResults />}
      </div>
    </div>
  );
};

export default App;