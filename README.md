# NkrsiSystem

Jest to projekt systemu kołowego zapewniającego obsługę kont członków, automatyczne wysyłanie zparoszeń do Slacka, otwieranie drzwi, uruchamianie rzutnika itp.

### Konfiguracja

Skopiuj plik nkrsiSystem/configDefault.py jako nkrsiSystem/config.py i uzupełnij odpowiednimi danymi.

Hasło do bazy danych musisz jednocześnie zmienić w docker-compose.yml w POSTGRES_PASSWORD.


### Uruchamianie zdokeryzowanego projektu

```
docker-compose up
```

Jeżeli jest to twoje pierwsze uruchomienie, to wymagane obrazy zostaną pobrane oraz zbudowane. Wszystkie potrzebne bazy zostaną utworzone wraz z superużytkownikiem o emailu SUPER_EMAIL i haśle SUPER_PASSWORD (wartości ustawiane w docker-compose.yml).

Po uruchomieniu powinniśmy mieć dostęp do serwisu przez:
```
localhost:80
```

### Endpoint dla sprawdzania id legitymacji
Stworzony z myślą o dostępie do Ślimaka. Aby uzyskać informację, czy dany użytkownik jest uprawniony, należy wysłąć żądanie POST na:
```
localhost/rest/card_id
```
z JSONem postaci:
```json
{
  "card_id": "id"
}
```
W odpowiedzi można otrzymać w wypadku powodzenia:
```json
{
  "ok": true
}
```
W wypadku niepowodzenia:
```json
{
  "ok": false
}
```
i status 404.