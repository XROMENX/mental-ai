import React, { useState, useEffect } from 'react';
import axios from 'axios';
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
    } catch (error) {
      localStorage.removeItem('token');
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
              className="w-full p-3 border rounded-lg text-right"
              required
            >
              <option value="">سطح تحصیلات</option>
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
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div 
          onClick={() => setCurrentPage('dass21')}
          className="bg-gradient-to-br from-blue-500 to-purple-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg transition-shadow"
        >
          <h3 className="text-xl font-bold text-right mb-2">آزمون DASS-21</h3>
          <p className="text-right opacity-90">ارزیابی افسردگی، اضطراب و استرس</p>
        </div>
        
        <div className="bg-gradient-to-br from-green-500 to-teal-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg transition-shadow">
          <h3 className="text-xl font-bold text-right mb-2">ثبت خلق و خو روزانه</h3>
          <p className="text-right opacity-90">امروز چطور احساس می‌کنید؟</p>
        </div>
        
        <div className="bg-gradient-to-br from-orange-500 to-red-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg transition-shadow">
          <h3 className="text-xl font-bold text-right mb-2">گپ با ربات مشاور</h3>
          <p className="text-right opacity-90">صحبت کردن می‌تواند کمک کند</p>
        </div>
        
        <div className="bg-gradient-to-br from-purple-500 to-pink-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg transition-shadow">
          <h3 className="text-xl font-bold text-right mb-2">نقشه راه سلامت روان</h3>
          <p className="text-right opacity-90">برنامه شخصی‌سازی شده برای بهبود</p>
        </div>
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
        <h2 className="text-2xl font-bold text-right">نتایج آزمون</h2>
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
        {currentPage === 'results' && <Results />}
      </div>
    </div>
  );
};

export default App;