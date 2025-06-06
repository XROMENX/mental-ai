import React from 'react';

const DASS21Test = ({ setCurrentPage, dass21Questions, dassResponses, setDassResponses, submitDASS21, loading }) => (
  <div className="bg-white rounded-lg p-8 shadow-lg max-w-4xl mx-auto">
    <div className="flex justify-between items-center mb-6">
      <button onClick={() => setCurrentPage('dashboard')} className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600">
        بازگشت
      </button>
      <h2 className="text-2xl font-bold text-right">آزمون DASS-21</h2>
    </div>
    <p className="text-right text-gray-600 mb-6">
      لطفاً هر سوال را با دقت بخوانید و بر اساس تجربه شما در هفته گذشته پاسخ دهید.
    </p>
    <div className="space-y-6">
      {dass21Questions.map(question => (
        <div key={question.id} className="border-b pb-4">
          <p className="text-right font-medium mb-3">{question.text}</p>
          <div className="flex justify-end space-x-4 space-x-reverse">
            {[
              { value: 0, label: 'اصلاً' },
              { value: 1, label: 'گاهی' },
              { value: 2, label: 'اغلب' },
              { value: 3, label: 'خیلی زیاد' },
            ].map(option => (
              <label key={option.value} className="flex items-center cursor-pointer">
                <span className="mr-2 text-sm">{option.label}</span>
                <input
                  type="radio"
                  name={`question_${question.id}`}
                  value={option.value}
                  checked={dassResponses[question.id] === option.value}
                  onChange={e => setDassResponses({ ...dassResponses, [question.id]: parseInt(e.target.value) })}
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

export default DASS21Test;
