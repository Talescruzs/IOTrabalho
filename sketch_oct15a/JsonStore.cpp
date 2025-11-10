#include "JsonStore.h"

JsonStore::JsonStore() {
  obj = JSONVar();
}

void JsonStore::set(const String& key, const String& value) {
  obj[key] = value;
}

void JsonStore::setNumber(const String& key, double value) {
  obj[key] = value;
}

void JsonStore::setBoolean(const String& key, bool value) {
  obj[key] = value;
}

void JsonStore::setObject(const String& key, const JSONVar& value) {
  obj[key] = value;
}

void JsonStore::remove(const String& key) {
  if (!JSON.typeof(obj[key]).equals("undefined")) {
    obj[key] = undefined;
  }
}

void JsonStore::clear() {
  obj = JSONVar();
}

void JsonStore::setNested(const String& parent, const String& child, const JSONVar& value) {
  if ((JSON.typeof(obj[parent])).equals("undefined")) {
    obj[parent] = JSONVar();
  }
  obj[parent][child] = value;
}

void JsonStore::setNested3(const String& k1, const String& k2, const String& k3, const JSONVar& value) {
  if ((JSON.typeof(obj[k1])).equals("undefined")) obj[k1] = JSONVar();
  if ((JSON.typeof(obj[k1][k2])).equals("undefined")) obj[k1][k2] = JSONVar();
  obj[k1][k2][k3] = value;
}

JSONVar JsonStore::get() const {
  return obj;
}

String JsonStore::toString() const {
  return JSON.stringify(obj);
}
