cluster_6: return cAvailableLocaleList.contains(locale);
cluster_8: return cAvailableLocaleSet == null || cAvailableLocaleSet.contains(locale);
cluster_2: boolean atLeastOnce = cAvailableLocaleSet.contains(locale); return atLeastOnce;
cluster_3: Locale.setDefault(locale); return false;
cluster_1: if (!cAvailableLocaleSet.contains(locale)) return false;
cluster_7: locale = Locale.ENGLISH; return cAvailableLocaleSet.contains(locale);
cluster_12: return this.locale.equals(locale) && cAvailableLocaleSet.contains(locale);
cluster_4: Locale locale = locale.getLocale(); return true;
cluster_5: if (locale == null) return false; return false;
cluster_11: Locale locale = (Locale) locale; return locale!= null;
cluster_9: if (locale.equals(locale)) return false; return cAvailableLocaleSet.contains(locale);
cluster_10: Locale locale = Locale.getDefault(); return cAvailableLocaleSet.contains(locale.getLocale());
cluster_13: try { return cAvailableLocaleSet.contains(locale); } catch (Exception e) { return false; }
