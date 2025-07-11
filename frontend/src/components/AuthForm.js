import React from 'react';

const REQUIRED_MESSAGE = 'لطفاً این فیلد را پر کنید';

const AuthForm = ({ authMode, setAuthMode, authData, setAuthData, handleAuth, loading, error }) => (
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
            onChange={e => setAuthData({ ...authData, fullName: e.target.value })}
            className="w-full p-3 border rounded-lg text-right"
            required
            onInvalid={e => e.target.setCustomValidity(REQUIRED_MESSAGE)}
            onInput={e => e.target.setCustomValidity('')}
          />
          <input
            type="number"
            placeholder="سن"
            value={authData.age}
            onChange={e => setAuthData({ ...authData, age: e.target.value })}
            className="w-full p-3 border rounded-lg text-right"
            required
            onInvalid={e => e.target.setCustomValidity(REQUIRED_MESSAGE)}
            onInput={e => e.target.setCustomValidity('')}
          />
          <select
            value={authData.studentLevel}
            onChange={e => setAuthData({ ...authData, studentLevel: e.target.value })}
            className="w-full p-3 border rounded-lg text-right cursor-pointer"
            required
            onInvalid={e => e.target.setCustomValidity(REQUIRED_MESSAGE)}
            onInput={e => e.target.setCustomValidity('')}
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
          onChange={e => setAuthData({ ...authData, email: e.target.value })}
          className="w-full p-3 border rounded-lg text-right"
          required
          onInvalid={e => e.target.setCustomValidity(REQUIRED_MESSAGE)}
          onInput={e => e.target.setCustomValidity('')}
        />
        <input
          type="password"
          placeholder="رمز عبور"
          value={authData.password}
          onChange={e => setAuthData({ ...authData, password: e.target.value })}
          className="w-full p-3 border rounded-lg text-right"
          required
          onInvalid={e => e.target.setCustomValidity(REQUIRED_MESSAGE)}
          onInput={e => e.target.setCustomValidity('')}
        />
      {authMode === 'register' && (
        <input
          type="password"
          placeholder="تکرار رمز عبور"
          value={authData.confirmPassword}
          onChange={e => setAuthData({ ...authData, confirmPassword: e.target.value })}
          className="w-full p-3 border rounded-lg text-right"
          required
          onInvalid={e => e.target.setCustomValidity(REQUIRED_MESSAGE)}
          onInput={e => e.target.setCustomValidity('')}
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

export default AuthForm;
