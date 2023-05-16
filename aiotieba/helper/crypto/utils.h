#ifdef __has_attribute
#define TBC_HAS_ATTRIBUTE(x) __has_attribute(x)
#else
#define TBC_HAS_ATTRIBUTE(x) 0
#endif

#if TBC_HAS_ATTRIBUTE(noescape)
#define TBC_NOESCAPE __attribute__((noescape))
#else
#define TBC_NOESCAPE
#endif
