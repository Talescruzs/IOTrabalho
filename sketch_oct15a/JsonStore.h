#ifndef JSON_STORE_H
#define JSON_STORE_H

#include <Arduino_JSON.h>

class JsonStore {
  private:
    JSONVar obj;
  public:
    JsonStore();

    // Modificadores de chave simples
    void set(const String& key, const String& value);
    void setNumber(const String& key, double value);
    void setBoolean(const String& key, bool value);
    void setObject(const String& key, const JSONVar& value);
    void remove(const String& key);
    void clear();

    // Modificadores aninhados (2 e 3 níveis)
    void setNested(const String& parent, const String& child, const JSONVar& value);
    void setNested3(const String& k1, const String& k2, const String& k3, const JSONVar& value);

    // Leitura
    JSONVar get() const;
    String toString() const;
};

#endif // JSON_STORE_H
