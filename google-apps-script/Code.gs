const EVENT_START = '2026-09-14';
const EVENT_END = '2026-09-21';
const CLASS_PERIODS = ['1교시', '2교시', '3교시', '4교시', '5교시', '6교시', '7교시'];
const AFTER_PERIOD = '방과후 1교시';
const SHEET_NAME = '예약';
const HEADERS = ['접수시간', '구분', '날짜', '교시', '선생님', '학급', '수업', '인원', '대표자', '참여자'];

function doGet() {
  return HtmlService.createHtmlOutputFromFile('Index')
    .setTitle('도서관 북크닉 예약')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

function getSheet_() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = spreadsheet.getSheetByName(SHEET_NAME);
  if (!sheet) sheet = spreadsheet.insertSheet(SHEET_NAME);
  if (sheet.getLastRow() === 0) sheet.appendRow(HEADERS);
  return sheet;
}

function getReservations() {
  const sheet = getSheet_();
  const rows = sheet.getDataRange().getValues().slice(1);
  return rows.filter(row => row[2]).map(row => ({
    type: String(row[1]), date: formatDate_(row[2]), period: String(row[3]),
    teacher: String(row[4] || ''), classroom: String(row[5] || ''),
    subject: String(row[6] || ''), students: Number(row[7] || 0),
    team: String(row[8] || ''), names: String(row[9] || '')
  }));
}

function saveReservation(reservation) {
  if (!reservation || !reservation.date) throw new Error('예약 날짜를 선택해 주세요.');
  if (reservation.date < EVENT_START || reservation.date > EVENT_END) throw new Error('행사 기간 내 날짜만 예약할 수 있습니다.');
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const reservations = getReservations();
    if (reservation.type === '수업') {
      const items = reservations.filter(item => item.type === '수업' && item.date === reservation.date && item.period === reservation.period);
      const people = items.reduce((sum, item) => sum + item.students, 0);
      if (!CLASS_PERIODS.includes(reservation.period)) throw new Error('올바른 수업 교시를 선택해 주세요.');
      if (!reservation.teacher || !reservation.classroom || !reservation.subject) throw new Error('선생님 이름, 학급, 수업을 모두 입력해 주세요.');
      if (items.length >= 2) throw new Error('이 교시는 이미 2개 반이 예약되었습니다.');
      if (people + Number(reservation.students) > 60) throw new Error(`현재 잔여 인원은 ${60 - people}명입니다.`);
      getSheet_().appendRow([new Date(), '수업', reservation.date, reservation.period, reservation.teacher, reservation.classroom, reservation.subject, Number(reservation.students), '', '']);
    } else {
      if (reservation.period !== AFTER_PERIOD) throw new Error('올바른 방과후 교시를 선택해 주세요.');
      const names = String(reservation.names || '').split(',').map(name => name.trim()).filter(Boolean);
      if (!reservation.team || names.length < 2 || names.length > 4 || names.length !== Number(reservation.students)) throw new Error('방과후 참여자 이름을 2~4명 정확히 입력해 주세요.');
      getSheet_().appendRow([new Date(), '방과후', reservation.date, AFTER_PERIOD, '', '', '', names.length, reservation.team, names.join(', ')]);
    }
    return getReservations();
  } finally {
    lock.releaseLock();
  }
}

function formatDate_(value) {
  return Utilities.formatDate(new Date(value), Session.getScriptTimeZone(), 'yyyy-MM-dd');
}
