import React from 'react';
import { LineChart, Line, BarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Dashboard = ({ handleLogout, user, gamification, todayMood, getMoodText, setCurrentPage, moodHistory, assessmentHistory }) => (
  <div className="bg-white rounded-lg p-8 shadow-lg">
    <div className="flex justify-between items-center mb-6">
      <button onClick={handleLogout} className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
        خروج
      </button>
      <h2 className="text-2xl font-bold text-right">خوش آمدید، {user?.full_name}</h2>
    </div>

    <div className="mb-6 text-right">
      <p className="font-bold">سطح {gamification.level}</p>
      <p className="text-sm">XP: {gamification.xp}</p>
      {gamification.badges.length > 0 && (
        <p className="text-sm">نشان‌ها: {gamification.badges.join(', ')}</p>
      )}
    </div>

    {todayMood && (
      <div className="mb-6 p-4 bg-green-50 rounded-lg border-right-4 border-green-500">
        <p className="text-right text-green-800">خلق و خوی امروز شما: {getMoodText(todayMood)} ثبت شده است</p>
      </div>
    )}

    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div onClick={() => setCurrentPage('dass21')} className="bg-gradient-to-br from-blue-500 to-purple-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg transition-shadow">
        <h3 className="text-xl font-bold text-right mb-2">آزمون DASS-21</h3>
        <p className="text-right opacity-90">ارزیابی افسردگی، اضطراب و استرس</p>
      </div>
      <div onClick={() => setCurrentPage('phq9')} className="bg-gradient-to-br from-indigo-500 to-blue-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg transition-shadow">
        <h3 className="text-xl font-bold text-right mb-2">آزمون PHQ-9</h3>
        <p className="text-right opacity-90">ارزیابی تخصصی افسردگی</p>
      </div>
      <div onClick={() => setCurrentPage('mood-tracker')} className="bg-gradient-to-br from-green-500 to-teal-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg transition-shadow">
        <h3 className="text-xl font-bold text-right mb-2">ثبت خلق و خو روزانه</h3>
        <p className="text-right opacity-90">امروز چطور احساس می‌کنید؟</p>
      </div>
      <div onClick={() => setCurrentPage('sleep-tracker')} className="bg-gradient-to-br from-teal-500 to-blue-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg transition-shadow">
        <h3 className="text-xl font-bold text-right mb-2">پیگیری خواب</h3>
        <p className="text-right opacity-90">ثبت مدت و کیفیت خواب</p>
      </div>
      <div onClick={() => setCurrentPage('daily-reflection')} className="bg-gradient-to-br from-yellow-500 to-orange-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg transition-shadow">
        <h3 className="text-xl font-bold text-right mb-2">یادداشت روزانه</h3>
        <p className="text-right opacity-90">نوشتن افکار و احساسات</p>
      </div>
      <div onClick={() => setCurrentPage('chatbot')} className="bg-gradient-to-br from-orange-500 to-red-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg transition-shadow">
        <h3 className="text-xl font-bold text-right mb-2">گپ با مشاور</h3>
        <p className="text-right opacity-90">صحبت کردن می‌تواند کمک کند</p>
      </div>
      <div onClick={() => setCurrentPage('mental-health-plan')} className="bg-gradient-to-br from-purple-500 to-pink-600 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg transition-shadow">
        <h3 className="text-xl font-bold text-right mb-2">نقشه راه سلامت روان</h3>
        <p className="text-right opacity-90">برنامه شخصی‌سازی شده برای بهبود</p>
      </div>
      <div onClick={() => setCurrentPage('history')} className="bg-gradient-to-br from-gray-500 to-gray-700 text-white p-6 rounded-lg cursor-pointer hover:shadow-lg transition-shadow">
        <h3 className="text-xl font-bold text-right mb-2">تاریخچه ارزیابی‌ها</h3>
        <p className="text-right opacity-90">مشاهده نتایج قبلی</p>
      </div>
    </div>

    {moodHistory.length > 0 && (
      <div className="mt-10">
        <h3 className="text-xl font-bold mb-4 text-right">روند خلق و خو</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={moodHistory.slice().reverse().map(entry => ({ date: new Date(entry.date).toLocaleDateString('fa-IR'), mood: entry.mood_level }))}>
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

    {assessmentHistory.some(a => a.assessment_type === 'DASS-21') && (
      <div className="mt-10">
        <h3 className="text-xl font-bold mb-4 text-right">آخرین نتیجه DASS-21</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={(function () {
            const latest = assessmentHistory.find(a => a.assessment_type === 'DASS-21');
            if (!latest) return [];
            return [
              { name: 'افسردگی', score: latest.results.depression_score },
              { name: 'اضطراب', score: latest.results.anxiety_score },
              { name: 'استرس', score: latest.results.stress_score },
            ];
          })()}>
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

export default Dashboard;
